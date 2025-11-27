from django.contrib import admin
from django.utils.html import format_html

from reservations.models import Table, Reservation
from .models import (Restaurant, Review, ContactMessage, MenuCategory,
                     MenuItem, SiteContent, TeamMember, Award)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']
    search_fields = ['name', 'address']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'address', 'phone', 'email', 'opening_hours')
        }),
        ('Главная страница', {
            'fields': ('hero_title', 'hero_subtitle')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'menu_items_count']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name']

    def menu_items_count(self, obj):
        return obj.menuitem_set.count()

    menu_items_count.short_description = 'Количество блюд'


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_popular', 'order']
    list_filter = ['category', 'is_available', 'is_popular']
    list_editable = ['price', 'is_available', 'is_popular', 'order']
    search_fields = ['name', 'description']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = 'Предпросмотр'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_rating_stars', 'created_at', 'is_approved', 'is_featured']
    list_filter = ['rating', 'is_approved', 'is_featured', 'created_at']
    list_editable = ['is_approved', 'is_featured']
    search_fields = ['user__username', 'comment']

    def get_rating_stars(self, obj):
        return obj.get_rating_stars()

    get_rating_stars.short_description = 'Рейтинг'
    get_rating_stars.allow_tags = True


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'order', 'is_active']
    list_filter = ['is_active', 'position']
    list_editable = ['position', 'order', 'is_active']
    search_fields = ['name', 'position']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = 'Предпросмотр'


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'order', 'is_active']
    list_filter = ['is_active', 'year']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'title', 'is_active', 'updated_at']
    list_filter = ['is_active', 'content_type']
    list_editable = ['is_active']
    search_fields = ['title', 'content']


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity', 'table_type', 'is_available']
    list_filter = ['table_type', 'is_available', 'capacity']
    search_fields = ['number']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'table', 'date', 'time', 'status']
    list_filter = ['status', 'date', 'table']
    search_fields = ['user__username', 'table__number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_processed']
    list_filter = ['is_processed', 'created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']
    list_editable = ['is_processed']
