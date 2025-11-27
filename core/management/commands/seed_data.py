from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import (Restaurant, Review, ContactMessage, MenuCategory,
                         MenuItem, SiteContent, TeamMember, Award)
from reservations.models import Table, Reservation

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Очистить базу данных перед заполнением',
        )

    def handle(self, *args, **options):

        if options['flush']:
            self.stdout.write('Очистка базы данных...')
            from django.core.management import call_command
            call_command('flush', interactive=False)

        self.stdout.write('Начало заполнения базы данных...')

        # Создание пользователей
        self.create_users()

        # Создание столиков
        tables = self.create_tables()

        # Создание меню
        self.create_menu()

        # Создание команды
        self.create_team()

        # Создание наград
        self.create_awards()

        # Создание контента сайта
        self.create_site_content()

        # Создание бронирований
        self.create_reservations(tables)

        # Создание отзывов
        self.create_reviews()

        # Создание сообщений
        self.create_contact_messages()

        self.stdout.write(
            self.style.SUCCESS('База данных успешно заполнена тестовыми данными!')
        )
        self.stdout.write('=' * 50)
        self.stdout.write('Тестовые учетные записи:')
        self.stdout.write('Администратор: admin / admin123')
        self.stdout.write('Менеджер: manager / manager123')
        self.stdout.write('Пользователь: testuser / testpass123')
        self.stdout.write('=' * 50)

    def create_users(self):
        """Создание тестовых пользователей"""
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@labellaitalia.ru',
                'password': 'admin123',
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'username': 'manager',
                'email': 'manager@labellaitalia.ru',
                'password': 'manager123',
                'first_name': 'Мария',
                'last_name': 'Иванова',
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'phone': '+7 (999) 123-45-67'
            },
        ]

        for user_data in users_data:
            username = user_data.pop('username')
            password = user_data.pop('password')

            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'Создан пользователь: {username}')

    def create_restaurant(self):
        """Создание ресторана"""
        restaurant, created = Restaurant.objects.get_or_create(
            name='La Bella Italia',
            defaults={
                'description': 'Аутентичный итальянский ресторан с атмосферой тепла и уюта. Мы предлагаем блюда традиционной итальянской кухни, приготовленные по старинным рецептам из свежайших ингредиентов.',
                'address': 'г. Москва, ул. Тверская, д. 15\nМетро: Тверская, Пушкинская, Чеховская',
                'phone': '+7 (495) 123-45-67',
                'email': 'info@labellaitalia.ru',
                'opening_hours': 'Пн-Чт: 11:00 - 23:00\nПт-Сб: 11:00 - 00:00\nВс: 11:00 - 22:00',
                'hero_title': 'Добро пожаловать в La Bella Italia',
                'hero_subtitle': 'Насладитесь аутентичной итальянской кухней в атмосфере тепла и уюта'
            }
        )
        if created:
            self.stdout.write('Создан ресторан: La Bella Italia')
        return restaurant

    def create_tables(self):
        """Создание столиков"""

        tables_data = [
            {'number': 'A1', 'capacity': 2, 'table_type': 'window', 'description': 'Уютный столик у окна'},
            {'number': 'A2', 'capacity': 2, 'table_type': 'standard', 'description': 'Стандартный столик для двоих'},
            {'number': 'A3', 'capacity': 4, 'table_type': 'standard', 'description': 'Столик для компании'},
            {'number': 'A4', 'capacity': 4, 'table_type': 'booth', 'description': 'Бутылочная зона'},
            {'number': 'B1', 'capacity': 6, 'table_type': 'standard', 'description': 'Большой стол для компании'},
            {'number': 'B2', 'capacity': 6, 'table_type': 'booth', 'description': 'Просторная бутылочная зона'},
            {'number': 'V1', 'capacity': 8, 'table_type': 'vip', 'description': 'VIP-зона'},
            {'number': 'V2', 'capacity': 4, 'table_type': 'vip', 'description': 'VIP-столик'},
        ]

        tables = []
        for table_data in tables_data:
            table, created = Table.objects.get_or_create(
                number=table_data['number'],
                defaults=table_data
            )
            if created:
                self.stdout.write(f'Создан столик: {table_data["number"]}')
            tables.append(table)

        return tables

    def create_menu(self):
        """Создание меню"""

        categories_data = [
            {'name': 'Антипасти', 'description': 'Традиционные итальянские закуски', 'order': 1},
            {'name': 'Паста', 'description': 'Свежая паста ручной работы', 'order': 2},
            {'name': 'Пицца', 'description': 'Тонкое тесто и натуральные ингредиенты', 'order': 3},
            {'name': 'Основные блюда', 'description': 'Мясные и рыбные блюда', 'order': 4},
            {'name': 'Десерты', 'description': 'Сладкие завершения трапезы', 'order': 5},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = MenuCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Создана категория: {cat_data["name"]}')
            categories[cat_data['name']] = category

        menu_items_data = [
            {
                'category': categories['Антипасти'],
                'name': 'Брускетта с помидорами',
                'description': 'Хрустящий хлеб с свежими томатами, базиликом и оливковым маслом',
                'price': 450,
                'is_popular': True,
                'ingredients': 'Хлеб чиабатта, помидоры черри, базилик, чеснок, оливковое масло',
                'cooking_time': 10
            },
            {
                'category': categories['Паста'],
                'name': 'Паста Карбонара',
                'description': 'Классическая римская паста с панчеттой, яйцами и пармезаном',
                'price': 890,
                'is_popular': True,
                'ingredients': 'Спагетти, панчетта, яйца, пармезан, черный перец',
                'cooking_time': 15
            },
            {
                'category': categories['Паста'],
                'name': 'Тальятелле с трюфелями',
                'description': 'Свежая тальятелле с трюфельным соусом и пармезаном',
                'price': 1200,
                'is_popular': False,
                'ingredients': 'Тальятелле, трюфельное масло, грибы, пармезан, сливки',
                'cooking_time': 12
            },
            {
                'category': categories['Пицца'],
                'name': 'Пицца Маргарита',
                'description': 'Тонкое тесто, соус из Сан-Марцано, моцарелла и базилик',
                'price': 750,
                'is_popular': True,
                'ingredients': 'Тесто для пиццы, томатный соус, моцарелла, базилик, оливковое масло',
                'cooking_time': 8
            },
            {
                'category': categories['Пицца'],
                'name': 'Пицца Четыре Сыра',
                'description': 'Нежное сочетание моцареллы, горгонзолы, пармезана и рикотты',
                'price': 850,
                'is_popular': False,
                'ingredients': 'Тесто для пиццы, моцарелла, горгонзола, пармезан, рикотта',
                'cooking_time': 10
            },
            {
                'category': categories['Основные блюда'],
                'name': 'Оссобуко',
                'description': 'Томленая телячья голяшка с ризотто и гремолатой',
                'price': 1650,
                'is_popular': True,
                'ingredients': 'Телячья голяшка, овощи, белое вино, бульон, ризотто, лимонная цедра',
                'cooking_time': 120
            },
            {
                'category': categories['Десерты'],
                'name': 'Тирамису',
                'description': 'Нежнейший десерт с кофе маскарпоне и саворди',
                'price': 450,
                'is_popular': True,
                'ingredients': 'Маскарпоне, саворди, кофе эспрессо, какао, яйца, сахар',
                'cooking_time': 0
            },
            {
                'category': categories['Десерты'],
                'name': 'Панна Котта',
                'description': 'Нежный сливочный десерт с ягодным соусом',
                'price': 380,
                'is_popular': False,
                'ingredients': 'Сливки, сахар, ваниль, желатин, ягодный соус',
                'cooking_time': 0
            },
            {
                'category': categories['Антипасти'],
                'name': 'Аранчини',
                'description': 'Жареные рисовые шарики с начинкой из моцареллы и мясного рагу',
                'price': 520,
                'is_popular': True,
                'ingredients': 'Рис, моцарелла, мясное рагу, панировочные сухари, яйцо',
                'cooking_time': 12
            },
            {
                'category': categories['Паста'],
                'name': 'Феттучине Альфредо',
                'description': 'Широкая паста с нежным сливочным соусом и пармезаном',
                'price': 780,
                'is_popular': False,
                'ingredients': 'Феттучине, сливки, пармезан, сливочное масло',
                'cooking_time': 10
            },
            {
                'category': categories['Пицца'],
                'name': 'Пицца Пепперони',
                'description': 'Острая пицца с салями и сыром моцарелла',
                'price': 890,
                'is_popular': True,
                'ingredients': 'Тесто, томатный соус, пепперони, моцарелла, орегано',
                'cooking_time': 9
            },
        ]

        for item_data in menu_items_data:
            item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                category=item_data['category'],
                defaults=item_data
            )
            if created:
                self.stdout.write(f'Создано блюдо: {item_data["name"]}')

    def create_team(self):
        """Создание команды"""
        team_data = [
            {
                'name': 'Марко Риччи',
                'position': 'Шеф-повар',
                'bio': 'Родился в Риме, обучался в кулинарной школе ALMA. Специализируется на римской и тосканской кухне. Более 15 лет опыта в лучших ресторанах Италии.',
                'order': 1,
                'instagram': 'https://instagram.com/chef_marco_ricci',
                'facebook': 'https://facebook.com/chefmarco',
                'linkedin': 'https://linkedin.com/in/marcoricci'
            },
            {
                'name': 'Анна Вольская',
                'position': 'Главный сомелье',
                'bio': 'Сертифицированный сомелье с 10-летним опытом. Специалист по итальянским винам. Победитель российского чемпионата сомелье 2022.',
                'order': 2,
                'instagram': 'https://instagram.com/sommelier_anna',
                'facebook': 'https://facebook.com/annasommelier',
                'linkedin': 'https://linkedin.com/in/annavolskaya'
            },
            {
                'name': 'Алексей Петров',
                'position': 'Управляющий',
                'bio': 'Опыт в ресторанном бизнесе более 12 лет. Создает незабываемый опыт для каждого гостя. Выпускник РЭУ им. Плеханова.',
                'order': 3,
                'instagram': 'https://instagram.com/manager_alex',
                'facebook': 'https://facebook.com/alexpetrovmanager',
                'linkedin': 'https://linkedin.com/in/alexeypetrov'
            },
        ]

        for member_data in team_data:
            member, created = TeamMember.objects.get_or_create(
                name=member_data['name'],
                position=member_data['position'],
                defaults=member_data
            )
            if created:
                self.stdout.write(f'Создан член команды: {member_data["name"]}')

    def create_awards(self):
        """Создание наград"""
        awards_data = [
            {'year': '2023', 'title': 'Звезда Michelin', 'description': 'За выдающееся качество кухни и сервиса',
             'order': 1},
            {'year': '2022', 'title': 'Лучший итальянский ресторан', 'description': 'Премия "Ресторанный Олимп"',
             'order': 2},
            {'year': '2021', 'title': 'Винная карта года', 'description': 'Награда от Wine Spectator', 'order': 3},
            {'year': '2020', 'title': 'Шеф-повар года', 'description': 'Марко Риччи - Gambero Rosso', 'order': 4},
            {'year': '2019', 'title': 'Эко-ресторан', 'description': 'За устойчивое развитие и экологичность',
             'order': 5},
            {'year': '2018', 'title': 'Выбор гостей', 'description': 'Лучший сервис по версии TripAdvisor', 'order': 6},
        ]

        for award_data in awards_data:
            award, created = Award.objects.get_or_create(
                year=award_data['year'],
                title=award_data['title'],
                defaults=award_data
            )
            if created:
                self.stdout.write(f'Создана награда: {award_data["year"]} - {award_data["title"]}')

    def create_site_content(self):
        """Создание контента сайта"""
        content_data = [
            {
                'content_type': 'about_mission',
                'title': 'Наша миссия',
                'content': 'Мы стремимся привнести подлинный вкус Италии в сердце Москвы, создавая атмосферу тепла, гостеприимства и кулинарного совершенства. Каждое блюдо в нашем ресторане - это история, рассказанная через вкус и аромат.'
            },
            {
                'content_type': 'about_history',
                'title': 'Наш путь',
                'content': 'От маленькой траттории до одного из лучших итальянских ресторанов Москвы. За 15 лет мы прошли incredible путь, сохраняя верность традициям и постоянно совершенствуясь.'
            },
            {
                'content_type': 'home_features',
                'title': 'Почему выбирают нас',
                'content': 'Наш ресторан сочетает в себе лучшие традиции итальянской кухни с современным подходом к обслуживанию. Мы используем только свежие продукты и готовим с любовью.'
            },
        ]

        for content_item in content_data:
            item, created = SiteContent.objects.get_or_create(
                content_type=content_item['content_type'],
                defaults=content_item
            )
            if created:
                self.stdout.write(f'Создан контент: {content_item["content_type"]}')

    def create_reservations(self, tables):
        """Создание бронирований"""
        user = User.objects.get(username='testuser')

        tomorrow = datetime.now().date() + timedelta(days=1)
        reservations_data = [
            {
                'table': tables[0],
                'date': tomorrow,
                'time': datetime.strptime('14:00', '%H:%M').time(),
                'duration': 2,
                'guests': 2,
                'status': 'confirmed',
                'special_requests': 'Столик у окна, пожалуйста'
            },
            {
                'table': tables[2],
                'date': tomorrow + timedelta(days=2),
                'time': datetime.strptime('19:00', '%H:%M').time(),
                'duration': 3,
                'guests': 4,
                'status': 'pending',
                'special_requests': 'День рождения'
            },
            {
                'table': tables[4],
                'date': datetime.now().date() - timedelta(days=5),
                'time': datetime.strptime('20:00', '%H:%M').time(),
                'duration': 2,
                'guests': 6,
                'status': 'completed',
                'special_requests': 'Корпоративный ужин'
            },
        ]

        for i, reservation_data in enumerate(reservations_data, 1):
            reservation, created = Reservation.objects.get_or_create(
                user=user,
                table=reservation_data['table'],
                date=reservation_data['date'],
                time=reservation_data['time'],
                defaults=reservation_data
            )
            if created:
                self.stdout.write(f'Создано бронирование #{i}')

    def create_reviews(self):
        """Создание отзывов"""
        user = User.objects.get(username='testuser')

        reviews_data = [
            {
                'rating': 5,
                'comment': 'Прекрасный ресторан! Паста была просто восхитительной. Обслуживание на высшем уровне.',
                'is_approved': True,
                'is_featured': True
            },
            {
                'rating': 4,
                'comment': 'Очень вкусная еда и приятная атмосфера. Пицца Маргарита - просто объедение!',
                'is_approved': True,
                'is_featured': True
            },
            {
                'rating': 5,
                'comment': 'Отмечали здесь годовщину свадьбы. Спасибо за прекрасный вечер! Особенно понравился десерт Тирамису.',
                'is_approved': True,
                'is_featured': True
            },
            {
                'rating': 3,
                'comment': 'Неплохой ресторан, но ожидал большего. Еда хорошая, но обслуживание могло бы быть лучше.',
                'is_approved': True,
                'is_featured': False
            },
            {
                'rating': 5,
                'comment': 'Лучший итальянский ресторан в городе! Обязательно вернемся снова.',
                'is_approved': True,
                'is_featured': False
            },
        ]

        for i, review_data in enumerate(reviews_data, 1):
            review, created = Review.objects.get_or_create(
                user=user,
                rating=review_data['rating'],
                comment=review_data['comment'],
                defaults=review_data
            )
            if created:
                self.stdout.write(f'Создан отзыв #{i} с рейтингом {review_data["rating"]}')

    def create_contact_messages(self):
        """Создание сообщений обратной связи"""
        messages_data = [
            {
                'name': 'Анна Смирнова',
                'email': 'anna@example.com',
                'subject': 'Вопрос о банкетах',
                'message': 'Здравствуйте! Хотим организовать корпоратив на 30 человек. Какие условия?'
            },
            {
                'name': 'Петр Иванов',
                'email': 'petr@example.com',
                'subject': 'Бронирование на праздник',
                'message': 'Добрый день! Интересует бронирование столика на День рождения.'
            },
            {
                'name': 'Ольга Козлова',
                'email': 'olga@example.com',
                'subject': 'Отзыв о посещении',
                'message': 'Были в вашем ресторане вчера. Очень понравилось! Особенно атмосфера и обслуживание.'
            },
        ]

        for msg_data in messages_data:
            message, created = ContactMessage.objects.get_or_create(
                email=msg_data['email'],
                subject=msg_data['subject'],
                defaults=msg_data
            )
            if created:
                self.stdout.write(f'Создано сообщение: {msg_data["subject"]}')
