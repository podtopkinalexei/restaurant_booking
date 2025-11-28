from django.core.cache import cache
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from ..filters import ReservationFilter
from ..models import Reservation, Table
from ..serializers import (
    ReservationSerializer, ReservationCreateSerializer,
    TableSerializer, TableAvailabilitySerializer
)
from ..services import ReservationService


class TableViewSet(viewsets.ModelViewSet):
    """ViewSet для управления столиками"""
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['table_type', 'capacity', 'is_available']
    search_fields = ['number', 'description']
    ordering_fields = ['number', 'capacity']
    ordering = ['number']

    def get_permissions(self):
        """Разрешения в зависимости от действия"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @method_decorator(cache_page(60 * 15))  # Кэшируем на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Доступные столики"""
        queryset = self.get_queryset().available()

        guests = request.query_params.get('guests')
        if guests:
            queryset = queryset.by_capacity(int(guests))


        table_type = request.query_params.get('table_type')
        if table_type:
            queryset = queryset.by_type(table_type)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def check_availability(self, request):
        """Проверка доступности столиков"""
        serializer = TableAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            available_tables = Table.objects.available_tables(
                data['date'], data['time'], data['duration'], data['guests']
            )

            if data.get('table_type'):
                available_tables = available_tables.by_type(data['table_type'])

            table_serializer = TableSerializer(available_tables, many=True)
            return Response({
                'available_tables': table_serializer.data,
                'count': available_tables.count()
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления бронированиями"""
    serializer_class = ReservationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReservationFilter
    search_fields = ['table__number', 'special_requests']
    ordering_fields = ['date', 'time', 'created_at']
    ordering = ['-date', '-time']

    def get_queryset(self):
        """Возвращает queryset в зависимости от прав пользователя"""
        if self.request.user.is_staff:
            return Reservation.objects.all().select_related('user', 'table')
        return Reservation.objects.filter(user=self.request.user).select_related('table')

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        """Создание бронирования с использованием сервиса"""
        try:
            reservation = ReservationService.create_reservation(
                user=self.request.user,
                table=serializer.validated_data['table'],
                date=serializer.validated_data['date'],
                time=serializer.validated_data['time'],
                duration=serializer.validated_data['duration'],
                guests=serializer.validated_data['guests'],
                special_requests=serializer.validated_data.get('special_requests', '')
            )
            # Обновляем instance сериализатора
            serializer.instance = reservation
        except ValueError as e:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'non_field_errors': [str(e)]})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отмена бронирования"""
        reservation = self.get_object()

        if reservation.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'У вас нет прав для отмены этого бронирования'},
                status=status.HTTP_403_FORBIDDEN
            )

        reservation.status = 'cancelled'
        reservation.save()

        cache.delete(f'user_reservations_{reservation.user.id}')

        return Response({'status': 'Бронирование отменено'})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Предстоящие бронирования"""
        queryset = self.get_queryset().filter(
            date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
