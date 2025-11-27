from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import ReservationForm, TableSelectionForm
from .models import Reservation, Table
from .services import ReservationService
from .tasks import send_reservation_confirmation


@login_required
def reservation_create(request):
    """Создание бронирования"""
    time_slots = generate_time_slots()
    tomorrow = timezone.now().date() + timedelta(days=1)
    reservation_form = ReservationForm(time_slots=time_slots)
    table_form = None

    context = {
        'time_slots': time_slots,
        'tomorrow': tomorrow,
        'reservation_form': reservation_form,
        'table_form': table_form,
        'available_tables': None,
        'form_data': {},
    }

    if request.method == 'POST':
        if 'check_availability' in request.POST:
            reservation_form = ReservationForm(request.POST, time_slots=time_slots)

            if reservation_form.is_valid():
                date = reservation_form.cleaned_data['date']
                time = reservation_form.cleaned_data['time']
                guests = reservation_form.cleaned_data['guests']
                duration = reservation_form.cleaned_data['duration']

                try:
                    time_obj = datetime.strptime(time, '%H:%M').time()
                    date_obj = date

                    if date_obj < timezone.now().date():
                        messages.error(request, 'Нельзя забронировать столик на прошедшую дату')
                    else:
                        available_tables = Table.get_available_tables(
                            date=date_obj,
                            time=time_obj,
                            duration=int(duration),
                            guests=int(guests)
                        )

                        table_form = TableSelectionForm(available_tables=available_tables)

                        context.update({
                            'reservation_form': reservation_form,
                            'table_form': table_form,
                            'available_tables': available_tables,
                            'form_data': reservation_form.cleaned_data,
                        })

                        if not available_tables:
                            messages.warning(request, 'К сожалению, на выбранное время нет свободных столиков')

                except ValueError as e:
                    messages.error(request, f'Ошибка в данных формы: {str(e)}')
            else:
                context['reservation_form'] = reservation_form

        elif 'create_reservation' in request.POST:
            date = request.POST.get('date')
            time = request.POST.get('time')
            guests = request.POST.get('guests')
            duration = request.POST.get('duration')
            table_id = request.POST.get('table')
            special_requests = request.POST.get('special_requests', '')

            if not all([table_id, date, time, guests]):
                messages.error(request, 'Пожалуйста, заполните все обязательные поля')

                reservation_form = ReservationForm(
                    initial={
                        'date': date,
                        'time': time,
                        'guests': guests,
                        'duration': duration
                    },
                    time_slots=time_slots
                )
                context['reservation_form'] = reservation_form
            else:
                try:
                    table = Table.objects.get(id=table_id)
                    time_obj = datetime.strptime(time, '%H:%M').time()
                    date_obj = datetime.strptime(date, '%Y-%m-%d').date()

                    available_tables = Table.get_available_tables(
                        date=date_obj,
                        time=time_obj,
                        duration=int(duration),
                        guests=int(guests)
                    )

                    if not available_tables.filter(id=table.id).exists():
                        messages.error(request, 'Выбранный столик больше не доступен')
                    else:
                        reservation = Reservation.objects.create(
                            user=request.user,
                            table=table,
                            date=date_obj,
                            time=time_obj,
                            duration=int(duration),
                            guests=int(guests),
                            special_requests=special_requests,
                            status='confirmed'
                        )

                        send_reservation_confirmation.delay(reservation.id)
                        messages.success(request, f'Бронирование #{reservation.id} успешно создано!')
                        return redirect('reservations:reservation_list')

                except Table.DoesNotExist:
                    messages.error(request, 'Выбранный столик не существует')
                except Exception as e:
                    messages.error(request, f'Ошибка при создании бронирования: {str(e)}')

    else:
        tomorrow = timezone.now().date() + timedelta(days=1)
        initial_data = {
            'date': tomorrow,
            'duration': 2,
            'guests': 2,
        }
        reservation_form = ReservationForm(initial=initial_data, time_slots=time_slots)
        context['reservation_form'] = reservation_form

    return render(request, 'reservations/reservation_create.html', context)


def generate_time_slots():
    """Генерирует список временных слотов"""
    times = []
    for hour in range(11, 22):  # с 11:00 до 22:00
        for minute in [0, 30]:  # каждые 30 минут
            times.append(f"{hour:02d}:{minute:02d}")
    return times


@login_required
def reservation_list(request):
    """Список бронирований пользователя"""
    user_reservations = ReservationService.get_user_reservations_with_details(request.user)
    active_reservations = []
    archived_reservations = []

    for reservation in user_reservations:
        if reservation.status in ['pending', 'confirmed'] and not reservation.is_past_due():
            active_reservations.append(reservation)
        else:
            archived_reservations.append(reservation)

    context = {
        'active_reservations': active_reservations,
        'archived_reservations': archived_reservations,
    }

    return render(request, 'reservations/reservation_list.html', context)


@login_required
def reservation_detail(request, pk):
    """Детальная информация о бронировании"""
    reservation = get_object_or_404(Reservation, pk=pk)

    if not request.user.is_staff and reservation.user != request.user:
        messages.error(request, 'У вас нет доступа к этому бронированию.')
        return redirect('reservations:reservation_list')

    context = {
        'reservation': reservation,
    }

    return render(request, 'reservations/reservation_detail.html', context)


@login_required
def reservation_cancel(request, pk):
    """Отмена бронирования пользователем"""
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if not reservation.can_be_cancelled():
        messages.error(request, 'Это бронирование нельзя отменить.')
        return redirect('reservations:reservation_list')

    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()

        messages.success(request, 'Бронирование успешно отменено.')
        return redirect('reservations:reservation_list')

    context = {
        'reservation': reservation,
    }

    return render(request, 'reservations/reservation_cancel.html', context)


@login_required
@permission_required('reservations.can_manage_all_reservations', raise_exception=True)
def reservation_management(request):
    """Управление бронированиями (для менеджеров)"""
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    reservations = Reservation.objects.all().select_related('user', 'table').order_by('-date', '-time')

    if status_filter:
        reservations = reservations.filter(status=status_filter)
    if date_filter:
        reservations = reservations.filter(date=date_filter)

    today = timezone.now().date()
    upcoming_reservations = reservations.filter(date__gte=today, status__in=['pending', 'confirmed'])
    past_reservations = reservations.filter(Q(date__lt=today) | Q(status__in=['cancelled', 'completed']))

    context = {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
        'status_choices': Reservation.STATUS_CHOICES,
        'current_status': status_filter,
        'current_date': date_filter,
    }

    return render(request, 'reservations/reservation_management.html', context)


@login_required
@permission_required('reservations.can_change_reservation_status', raise_exception=True)
def reservation_change_status(request, pk):
    """Изменение статуса бронирования (для менеджеров)"""
    reservation = get_object_or_404(Reservation, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Reservation.STATUS_CHOICES).keys():
            reservation.status = new_status
            reservation.save()

            messages.success(request, f'Статус бронирования изменен на {reservation.get_status_display()}')

    return redirect('reservations:reservation_management')


def reservation_success(request):
    """Страница успешного бронирования"""
    return render(request, 'reservations/reservation_success.html')
