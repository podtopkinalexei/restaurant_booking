from datetime import datetime, timedelta

from reservations.models import Table, Reservation


def find_available_tables(date, time, duration, guests, table_type=None):
    """Находит доступные столики по заданным параметрам"""

    tables = Table.objects.filter(
        capacity__gte=guests,
        is_available=True
    )

    if table_type:
        tables = tables.filter(table_type=table_type)

    available_tables = []

    for table in tables:
        is_available, message = table.is_available_for_reservation(date, time, duration)
        if is_available:
            available_tables.append({
                'table': table,
                'message': message
            })

    return available_tables


def get_available_time_slots(table, date, opening_time="11:00", closing_time="23:00"):
    """Возвращает список доступных временных слотов для столика на указанную дату"""
    available_slots = []

    # Преобразуем время открытия и закрытия
    open_time = datetime.strptime(opening_time, "%H:%").time()
    close_time = datetime.strptime(closing_time, "%H:%").time()

    # Получаем все бронирования для этого столика на указанную дату
    reservations = Reservation.objects.filter(
        table=table,
        date=date,
        status__in=['pending', 'confirmed']
    ).order_by('time')

    # Начинаем с времени открытия
    current_time = open_time

    while current_time < close_time:
        # Проверяем доступность для стандартной продолжительности (2 часа)
        is_available, message = table.is_available_for_reservation(
            date, current_time, 2
        )

        if is_available:
            available_slots.append({
                'time': current_time,
                'display': current_time.strftime('%H:%M')
            })

        # Переходим к следующему временному слоту (каждые 30 минут)
        current_time_dt = datetime.combine(date, current_time)
        current_time_dt += timedelta(minutes=30)
        current_time = current_time_dt.time()

        # Если вышли за время закрытия, выходим из цикла
        if current_time >= close_time:
            break

    return available_slots
