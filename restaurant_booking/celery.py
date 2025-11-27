import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_booking.settings')

app = Celery('restaurant_booking')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-reservation-reminders': {
        'task': 'reservations.tasks.send_reservation_reminder',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
    'cleanup-old-reservations': {
        'task': 'reservations.tasks.cleanup_old_reservations',
        'schedule': crontab(hour=0, minute=0, day_of_month='1'),  # Первое число каждого месяца
    },
    'auto-confirm-reservations': {
        'task': 'reservations.tasks.auto_confirm_reservations',
        'schedule': crontab(minute='*/30'),  # Каждые 30 минут
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
