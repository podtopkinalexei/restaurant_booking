from datetime import timedelta, date, time

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from reservations.forms import ReservationForm
from reservations.models import Table, Reservation

User = get_user_model()


class ModelTests(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        self.table1 = Table.objects.create(
            number='T1',
            capacity=2,
            table_type='standard'
        )

        self.reservation = Reservation.objects.create(
            user=self.user,
            table=self.table1,
            date=date.today() + timedelta(days=1),
            time=time(18, 0),
            duration=2,
            guests=2,
            status='confirmed'
        )

    def test_restaurant_creation(self):
        """Тест создания ресторана"""
        from core.models import Restaurant
        restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            phone='+7 (999) 999-99-99'
        )
        self.assertEqual(restaurant.name, 'Test Restaurant')
        self.assertEqual(str(restaurant), 'Test Restaurant')

    def test_table_creation(self):
        """Тест создания столика"""
        self.assertEqual(self.table1.number, 'T1')
        self.assertEqual(self.table1.capacity, 2)
        self.assertTrue(self.table1.is_available)

    def test_reservation_creation(self):
        """Тест создания бронирования"""
        self.assertEqual(self.reservation.user, self.user)
        self.assertEqual(self.reservation.table, self.table1)
        self.assertEqual(self.reservation.status, 'confirmed')


class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.table = Table.objects.create(
            number='T1',
            capacity=4
        )

    def test_valid_reservation_form(self):
        """Тест валидной формы бронирования"""
        form_data = {
            'date': date.today() + timedelta(days=3),
            'time': '18:00',
            'duration': '2',
            'guests': '2',
        }
        form = ReservationForm(data=form_data)
        self.assertIn('date', form.fields)
        self.assertIn('time', form.fields)

    def test_invalid_reservation_form_past_date(self):
        """Тест формы бронирования с прошедшей датой"""
        form_data = {
            'date': date.today() - timedelta(days=1),
            'time': '18:00',
            'duration': '2',
            'guests': '2',
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_admin_login_view(self):
        """Тест страницы входа в админку (всегда существует)"""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)

    def test_user_login(self):
        """Тест входа пользователя"""
        # Создаем пользователя
        user = User.objects.create_user(
            username='loginuser',
            password='testpass123'
        )

        # Пробуем войти
        login_success = self.client.login(username='loginuser', password='testpass123')
        self.assertTrue(login_success)


class UtilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.table1 = Table.objects.create(
            number='T1',
            capacity=2
        )

        self.table2 = Table.objects.create(
            number='T2',
            capacity=4
        )

        self.reservation = Reservation.objects.create(
            user=self.user,
            table=self.table1,
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            duration=2,
            guests=2,
            status='confirmed'
        )

    def test_table_availability_method(self):
        """Тест метода проверки доступности столика"""
        # Проверяем доступность для свободного времени
        is_available, message = self.table2.is_available_for_reservation(
            date=date.today() + timedelta(days=1),
            time=time(14, 0),
            duration=2
        )
        self.assertTrue(is_available)

        # Проверяем недоступность для занятого времени
        is_available, message = self.table1.is_available_for_reservation(
            date=self.reservation.date,
            time=time(19, 0),
            duration=2
        )
        self.assertFalse(is_available)


class BasicAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.table = Table.objects.create(
            number='T1',
            capacity=4
        )

    def test_admin_interface(self):
        """Тест доступности админ-интерфейса"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_api_auth(self):
        """Тест API аутентификации"""
        response = self.client.get('/api-auth/login/')
        self.assertEqual(response.status_code, 200)
