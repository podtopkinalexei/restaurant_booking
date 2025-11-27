from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Table(models.Model):
    """Модель столика"""
    TABLE_TYPES = [
        ('standard', 'Стандартный'),
        ('booth', 'Бутылочный'),
        ('window', 'У окна'),
        ('vip', 'VIP'),
    ]

    number = models.CharField(max_length=10, verbose_name="Номер столика", unique=True)
    capacity = models.PositiveIntegerField(
        verbose_name="Вместимость",
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    table_type = models.CharField(
        max_length=20,
        choices=TABLE_TYPES,
        default='standard',
        verbose_name="Тип столика"
    )
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"
        permissions = [
            ("can_manage_tables", "Может управлять столиками"),
        ]

    def __str__(self):
        return f"Столик {self.number} ({self.capacity} персон)"

    @classmethod
    def get_available_tables(cls, date, time, duration, guests):
        """Находит доступные столики - возвращает QuerySet"""
        start_time = datetime.combine(date, time)
        end_time = start_time + timedelta(hours=duration)

        potential_tables = cls.objects.filter(
            is_available=True,
            capacity__gte=guests)

        conflicting_table_ids = []
        for table in potential_tables:
            conflicting_reservations = table.reservations.filter(
                date=date,
                status__in=['pending', 'confirmed']
            )

            for reservation in conflicting_reservations:
                reservation_start = datetime.combine(date, reservation.time)
                reservation_end = reservation_start + timedelta(hours=reservation.duration)

                if (start_time < reservation_end and end_time > reservation_start):
                    conflicting_table_ids.append(table.id)
                    break

        return potential_tables.exclude(id__in=conflicting_table_ids)

    def is_available_for_reservation(self, date, time, duration):
        """Проверяет доступность столика для бронирования"""
        if not self.is_available:
            return False, "Столик недоступен"

        start_time = datetime.combine(date, time)
        end_time = start_time + timedelta(hours=duration)

        conflicting_reservations = self.reservations.filter(
            date=date,
            status__in=['pending', 'confirmed']
        )

        for reservation in conflicting_reservations:
            reservation_start = datetime.combine(date, reservation.time)
            reservation_end = reservation_start + timedelta(hours=reservation.duration)

            if (start_time < reservation_end and end_time > reservation_start):
                return False, f"Столик занят с {reservation.time} до {reservation_end.time()}"

        return True, "Столик доступен"


class Reservation(models.Model):
    """Модель бронирования"""
    STATUS_CHOICES = [
        ('pending', 'Ожидание подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='reservations'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        verbose_name="Столик",
        related_name='reservations'
    )
    date = models.DateField(verbose_name="Дата бронирования")
    time = models.TimeField(verbose_name="Время бронирования")
    duration = models.PositiveIntegerField(
        default=2,
        verbose_name="Продолжительность (часы)",
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    guests = models.PositiveIntegerField(
        verbose_name="Количество гостей",
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    special_requests = models.TextField(blank=True, verbose_name="Особые пожелания")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-date', '-time']
        permissions = [
            ("can_manage_all_reservations", "Может управлять всеми бронированиями"),
            ("can_change_reservation_status", "Может изменять статус бронирования"),
        ]

    def __str__(self):
        return f"Бронирование #{self.id} - {self.user.username} - {self.date} {self.time}"

    @property
    def end_time(self):
        """Вычисляемое время окончания бронирования"""
        start_datetime = datetime.combine(self.date, self.time)
        end_datetime = start_datetime + timedelta(hours=self.duration)
        return end_datetime.time()

    def is_past_due(self):
        """Проверяет, прошла ли дата бронирования"""
        from django.utils import timezone
        reservation_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return timezone.now() > reservation_datetime

    def can_be_cancelled(self):
        """Проверяет, можно ли отменить бронирование"""
        from django.utils import timezone
        reservation_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        # Можно отменить только если до бронирования больше 1 часа
        return (not self.is_past_due() and
                self.status in ['pending', 'confirmed'] and
                (reservation_datetime - timezone.now()).total_seconds() > 3600)
