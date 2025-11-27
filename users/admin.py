from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_manager', 'is_verified')
    list_filter = ('is_staff', 'is_manager', 'is_verified', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'date_of_birth', 'avatar', 'is_manager', 'is_verified')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
    )
