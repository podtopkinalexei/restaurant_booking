from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from reservations.models import Table
from .forms import ReviewForm
from .models import Restaurant, Review, ContactMessage, MenuItem, SiteContent, TeamMember, Award, MenuCategory
from .utils import find_available_tables, get_available_time_slots


# @cache_page(60 * 15)
def home(request):
    """Главная страница"""
    restaurant = Restaurant.objects.first()
    reviews = Review.objects.filter(is_approved=True, is_featured=True)[:3]

    popular_items = MenuItem.objects.filter(
        is_available=True,
        is_popular=True
    )[:4]  # Ограничиваем 4 блюдами для главной

    features_content = SiteContent.objects.filter(
        content_type='home_features',
        is_active=True
    ).first()

    context = {
        'restaurant': restaurant,
        'reviews': reviews,
        'popular_items': popular_items,
        'features_content': features_content,
    }
    return render(request, 'core/home.html', context)


# @cache_page(60 * 30)
def about(request):
    """Страница о ресторане"""
    restaurant = Restaurant.objects.first()
    team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    awards = Award.objects.filter(is_active=True).order_by('-year', 'order')

    mission_content = SiteContent.objects.filter(
        content_type='about_mission',
        is_active=True
    ).first()

    history_content = SiteContent.objects.filter(
        content_type='about_history',
        is_active=True
    ).first()

    context = {
        'restaurant': restaurant,
        'team_members': team_members,
        'awards': awards,
        'mission_content': mission_content,
        'history_content': history_content,
    }
    return render(request, 'core/about.html', context)


def menu(request):
    """Страница меню ресторана"""
    categories = MenuCategory.objects.filter(
        is_active=True
    ).prefetch_related('menuitem_set').order_by('order')

    popular_items = MenuItem.objects.filter(
        is_available=True,
        is_popular=True
    )[:6]  # Ограничиваем 6 блюдами

    context = {
        'categories': categories,
        'popular_items': popular_items,
    }
    return render(request, 'core/menu.html', context)


def check_availability(request):
    """API endpoint для проверки доступности столиков (AJAX)"""
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')
        duration = request.GET.get('duration', 2)
        guests = request.GET.get('guests', 2)
        table_type = request.GET.get('table_type')

        try:
            reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            reservation_time = datetime.strptime(time_str, '%H:%M').time()
            duration = int(duration)
            guests = int(guests)

            # Проверяем, что дата не в прошлом
            if reservation_date < timezone.now().date():
                return JsonResponse({
                    'success': False,
                    'message': 'Нельзя выбрать прошедшую дату'
                })

            available_tables_data = find_available_tables(
                reservation_date, reservation_time, duration, guests, table_type
            )

            available_tables = []
            for table_data in available_tables_data:
                table = table_data['table']
                available_tables.append({
                    'id': table.id,
                    'number': table.number,
                    'capacity': table.capacity,
                    'table_type': table.get_table_type_display(),
                    'description': table.description,
                    'message': table_data['message']
                })

            return JsonResponse({
                'success': True,
                'available_tables': available_tables,
                'count': len(available_tables)
            })

        except (ValueError, TypeError) as e:
            return JsonResponse({
                'success': False,
                'message': 'Неверные параметры запроса'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def get_available_times(request):
    """API endpoint для получения доступных временных слотов (AJAX)"""
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        date_str = request.GET.get('date')
        table_id = request.GET.get('table_id')

        try:
            reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            table = Table.objects.get(id=table_id)

            available_slots = get_available_time_slots(table, reservation_date)

            return JsonResponse({
                'success': True,
                'available_times': available_slots
            })

        except (ValueError, TypeError, Table.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'message': 'Неверные параметры запроса'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def feedback(request):
    """Обработка формы обратной связи из футера (только для авторизованных пользователей)"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        message_text = request.POST.get('message', '').strip()
        email = request.user.email

        if not name or not message_text:
            messages.error(request, 'Пожалуйста, заполните все поля формы.')
            return redirect(request.META.get('HTTP_REFERER', 'core:home'))

        try:
            contact_message = ContactMessage.objects.create(
                user=request.user,
                name=name,
                email=email,
                subject="Обратная связь с сайта",  # Автоматическая тема
                message=message_text
            )

            send_feedback_notification(contact_message)
            messages.success(request, 'Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.')

        except Exception as e:
            print(f"Ошибка при сохранении обратной связи: {e}")
            messages.error(request, 'Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.')

        return redirect(request.META.get('HTTP_REFERER', 'core:home'))

    return redirect('core:home')


def send_feedback_notification(contact_message):
    """Отправка уведомления о новой обратной связи"""
    try:
        subject = f'Новое сообщение обратной связи от {contact_message.name}'
        message = f'''
        Поступило новое сообщение обратной связи:

        От: {contact_message.name}
        Email: {contact_message.email}
        Пользователь: {contact_message.user.username if contact_message.user else "Неавторизован"}
        Дата: {contact_message.created_at.strftime("%d.%m.%Y %H:%M")}
        Тема: {contact_message.subject}

        Сообщение:
        {contact_message.message}
        '''

        # Отправляем на email ресторана
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Ошибка при отправке email уведомления: {e}")


@login_required
def add_review(request):
    """Добавление отзыва"""

    existing_review = Review.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()

            messages.success(request, 'Спасибо за ваш отзыв! Он будет опубликован после проверки.')
            return redirect('core:reviews')
    else:
        if existing_review:
            form = ReviewForm(instance=existing_review)
        else:
            form = ReviewForm()

    context = {
        'form': form,
        'existing_review': existing_review
    }
    return render(request, 'core/add_review.html', context)


def reviews_list(request):
    """Страница со всеми отзывами"""
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0

    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()

    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'average_rating': round(average_rating, 1),
        'rating_distribution': rating_distribution,
    }
    return render(request, 'core/reviews.html', context)


@login_required
def delete_review(request, review_id):
    """Удаление отзыва"""
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Ваш отзыв был удален.')
        return redirect('core:reviews')

    return render(request, 'core/delete_review.html', {'review': review})
