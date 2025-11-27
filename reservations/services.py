from django.db import transaction

from .models import Reservation, Table
from .tasks import send_reservation_confirmation


class ReservationService:
    """Сервис для работы с бронированиями"""

    @staticmethod
    @transaction.atomic
    def create_reservation(user, table, date, time, duration, guests, special_requests=''):
        """Создание бронирования с транзакцией"""
        available_tables = Table.get_available_tables(date, time, duration, guests)

        if not available_tables.filter(id=table.id).exists():
            raise ValueError("Столик недоступен для бронирования")

        reservation = Reservation.objects.create(
            user=user,
            table=table,
            date=date,
            time=time,
            duration=duration,
            guests=guests,
            special_requests=special_requests,
            status='confirmed'
        )

        send_reservation_confirmation.delay(reservation.id)

        return reservation

    @staticmethod
    def get_user_reservations_with_details(user):
        """Получение бронирований пользователя с детальной информацией"""
        return Reservation.objects.filter(user=user).select_related(
            'table'
        ).order_by('-date', '-time')
