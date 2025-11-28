from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.safestring import mark_safe


class Restaurant(models.Model):
    """Модель ресторана"""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    opening_hours = models.CharField(max_length=100, verbose_name="Часы работы")
    hero_title = models.CharField(max_length=200, default="Добро пожаловать в La Bella Italia",
                                  verbose_name="Заголовок на главной")
    hero_subtitle = models.TextField(default="Насладитесь аутентичной итальянской кухней в атмосфере тепла и уюта",
                                     verbose_name="Подзаголовок на главной")

    # SEO поля
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Meta title")
    meta_description = models.TextField(blank=True, verbose_name="Meta description")

    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"

    def __str__(self):
        return self.name


class MenuCategory(models.Model):
    """Категории меню"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Категория меню"
        verbose_name_plural = "Категории меню"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Блюда в меню"""
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True, verbose_name="Изображение")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")
    is_popular = models.BooleanField(default=False, verbose_name="Популярное блюдо")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    ingredients = models.TextField(blank=True, verbose_name="Ингредиенты")
    cooking_time = models.PositiveIntegerField(blank=True, null=True, verbose_name="Время приготовления (мин)")

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ['category__order', 'order', 'name']

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва"""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.PositiveIntegerField(
        verbose_name="Рейтинг",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=[(1, '1 звезда'), (2, '2 звезды'), (3, '3 звезды'), (4, '4 звезды'), (5, '5 звезд')]
    )
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")
    is_featured = models.BooleanField(default=False, verbose_name="Показывать на главной")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.user.username} - {self.rating} звезд"

    def get_rating_stars(self):
        """Возвращает HTML для отображения звезд рейтинга"""
        stars = ''
        for i in range(1, 6):
            if i <= self.rating:
                stars += '<i class="bi bi-star-fill text-warning"></i>'
            else:
                stars += '<i class="bi bi-star text-warning"></i>'
        return mark_safe(stars)


class SiteContent(models.Model):
    """Управление контентом сайта"""
    CONTENT_TYPES = [
        ('about_mission', 'Миссия на странице "О нас"'),
        ('about_history', 'История на странице "О нас"'),
        ('about_team', 'Команда на странице "О нас"'),
        ('home_features', 'Преимущества на главной'),
        ('contact_info', 'Контактная информация'),
    ]

    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES, unique=True, verbose_name="Тип контента")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Контент сайта"
        verbose_name_plural = "Контент сайта"

    def __str__(self):
        return self.get_content_type_display()


class TeamMember(models.Model):
    """Члены команды"""
    name = models.CharField(max_length=100, verbose_name="Имя")
    position = models.CharField(max_length=100, verbose_name="Должность")
    bio = models.TextField(verbose_name="Биография")
    image = models.ImageField(upload_to='team/', verbose_name="Фото")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    instagram = models.URLField(blank=True, verbose_name="Instagram")
    facebook = models.URLField(blank=True, verbose_name="Facebook")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")

    class Meta:
        verbose_name = "Член команды"
        verbose_name_plural = "Члены команды"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.position}"


class Award(models.Model):
    """Награды ресторана"""
    year = models.CharField(max_length=10, verbose_name="Год")
    title = models.CharField(max_length=200, verbose_name="Название награды")
    description = models.TextField(verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Награда"
        verbose_name_plural = "Награды"
        ordering = ['-year', 'order']

    def __str__(self):
        return f"{self.year} - {self.title}"


class ContactMessage(models.Model):
    """Модель сообщения из формы обратной связи"""
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь"
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, blank=True, default="Обратная связь", verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Сообщение от {self.user.username} - {self.subject}"
        return f"Сообщение от {self.name} - {self.subject}"
