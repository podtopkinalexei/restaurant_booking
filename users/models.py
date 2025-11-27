from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    is_manager = models.BooleanField(default=False, verbose_name="Менеджер")
    is_verified = models.BooleanField(default=False, verbose_name="Подтвержденный email")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_manage_reservations", "Может управлять бронированиями"),
            ("can_manage_users", "Может управлять пользователями"),
            ("can_view_reports", "Может просматривать отчеты"),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"
