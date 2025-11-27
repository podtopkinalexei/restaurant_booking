from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from reservations.models import Reservation
from .forms import UserProfileForm, CustomUserCreationForm


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('core:home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """Личный кабинет пользователя"""
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-date', '-time')

    if 'update' in request.GET:
        form = UserProfileForm(instance=request.user)
        return render(request, 'users/profile.html', {
            'form': form,
            'reservations': user_reservations,
            'show_form': True
        })

    context = {
        'reservations': user_reservations,
        'show_form': False
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_update(request):
    """Обновление профиля пользователя"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserProfileForm(instance=request.user)

    user_reservations = Reservation.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'users/profile.html', {
        'form': form,
        'reservations': user_reservations,
        'show_form': True
    })


def custom_logout(request):
    """Кастомный выход из системы"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')
        return redirect('core:home')
    else:
        return render(request, 'users/logout_confirm.html')
