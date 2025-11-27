from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Reservation


@shared_task
def send_reservation_confirmation(reservation_id):
    """Отправка подтверждения бронирования"""
    try:
        reservation = Reservation.objects.get(id=reservation_id)

        subject = f'Подтверждение бронирования #{reservation.id}'
        message = f'''
        Уважаемый(ая) {reservation.user.get_full_name() or reservation.user.username},

        Ваше бронирование подтверждено:
        Дата: {reservation.date}
        Время: {reservation.time}
        Столик: {reservation.table.number}
        Гостей: {reservation.guests}
        Статус: {reservation.get_status_display()}

        Спасибо за выбор нашего ресторана!
        '''

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [reservation.user.email],
            fail_silently=False,
        )

        return f'Email отправлен для бронирования {reservation_id}'
    except Reservation.DoesNotExist:
        return f'Бронирование {reservation_id} не найдено'


@shared_task
def send_reservation_reminder():
    """Напоминание о бронировании за день"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    reservations = Reservation.objects.filter(
        date=tomorrow,
        status='confirmed'
    )

    for reservation in reservations:
        subject = f'Напоминание о бронировании #{reservation.id}'
        message = f'''
        Напоминаем о вашем бронировании на завтра:
        Дата: {reservation.date}
        Время: {reservation.time}
        Столик: {reservation.table.number}

        Ждем вас в нашем ресторане!
        '''

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [reservation.user.email],
            fail_silently=True,
        )

    return f'Отправлено напоминаний: {reservations.count()}'


@shared_task
def auto_confirm_pending_reservations():
    """Автоматическое подтверждение бронирований со статусом pending"""
    try:
        confirmed_count = Reservation.objects.filter(
            status='pending',
            date__gte=timezone.now().date()
        ).update(status='confirmed')

        confirmed_reservations = Reservation.objects.filter(
            status='confirmed',
            updated_at__gte=timezone.now() - timedelta(minutes=10)
        )

        for reservation in confirmed_reservations:
            send_reservation_confirmation.delay(reservation.id)

        return f'Автоматически подтверждено бронирований: {confirmed_count}'
    except Exception as e:
        return f'Ошибка при автоматическом подтверждении: {str(e)}'


@shared_task
def cleanup_old_reservations():
    """Очистка старых завершенных бронирований"""
    cutoff_date = timezone.now().date() - timedelta(days=365)  # 1 год назад
    deleted_count = Reservation.objects.filter(
        date__lt=cutoff_date,
        status__in=['completed', 'cancelled']
    ).delete()[0]

    return f'Удалено старых бронирований: {deleted_count}'
