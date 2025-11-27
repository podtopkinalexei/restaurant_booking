from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('menu/', views.menu, name='menu'),
    path('reviews/', views.reviews_list, name='reviews'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/check-availability/', views.check_availability, name='check_availability'),
    path('api/get-available-times/', views.get_available_times, name='get_available_times'),
    path('feedback/', views.feedback, name='feedback'),
]
