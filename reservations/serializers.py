from rest_framework import serializers

from users.models import CustomUser
from .models import Reservation, Table


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone']
        read_only_fields = ['id']


class TableSerializer(serializers.ModelSerializer):
    """Сериализатор для столика"""
    reservation_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Table
        fields = [
            'id', 'number', 'capacity', 'table_type',
            'is_available', 'description', 'reservation_count'
        ]
        read_only_fields = ['id']


class ReservationSerializer(serializers.ModelSerializer):
    """Сериализатор для бронирования"""
    user = UserSerializer(read_only=True)
    table = TableSerializer(read_only=True)
    table_id = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.all(),
        source='table',
        write_only=True
    )

    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'table', 'table_id', 'date', 'time',
            'duration', 'guests', 'special_requests', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, data):
        """Валидация данных бронирования"""
        date = data.get('date')
        time = data.get('time')
        duration = data.get('duration')
        table = data.get('table')
        guests = data.get('guests')

        if date and time and duration and table:
            # Проверка доступности столика
            is_available, message = table.is_available_for_reservation(
                date, time, duration
            )
            if not is_available:
                raise serializers.ValidationError({'table': message})

            # Проверка вместимости
            if guests > table.capacity:
                raise serializers.ValidationError({
                    'guests': f'Максимальная вместимость столика: {table.capacity}'
                })

        return data


class ReservationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания бронирования"""

    class Meta:
        model = Reservation
        fields = ['table', 'date', 'time', 'duration', 'guests', 'special_requests']

    def create(self, validated_data):
        """Создание бронирования с текущим пользователем"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TableAvailabilitySerializer(serializers.Serializer):
    """Сериализатор для проверки доступности столиков"""
    date = serializers.DateField()
    time = serializers.TimeField()
    duration = serializers.IntegerField(min_value=1, max_value=6)
    guests = serializers.IntegerField(min_value=1, max_value=12)
    table_type = serializers.ChoiceField(
        choices=Table.TABLE_TYPES,
        required=False,
        allow_null=True
    )

    def validate_date(self, value):
        """Валидация даты"""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Нельзя выбрать прошедшую дату")
        return value
