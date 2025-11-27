from django.urls import path

from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.reservation_create, name='reservation_create'),
    path('list/', views.reservation_list, name='reservation_list'),
    path('detail/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('cancel/<int:pk>/', views.reservation_cancel, name='reservation_cancel'),
    path('management/', views.reservation_management, name='reservation_management'),
    path('status/<int:pk>/change/', views.reservation_change_status, name='reservation_change_status'),
    path('success/', views.reservation_success, name='reservation_success'),
]
