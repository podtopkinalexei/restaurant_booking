from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Table


class ReservationForm(forms.Form):
    """Форма для бронирования столика"""

    date = forms.DateField(
        label='Дата посещения *',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        })
    )

    time = forms.ChoiceField(
        label='Время *',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    guests = forms.ChoiceField(
        label='Количество гостей *',
        choices=[(i, f'{i} человек') for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    duration = forms.ChoiceField(
        label='Продолжительность',
        choices=[
            (1, '1 час'),
            (2, '2 часа (стандартно)'),
            (3, '3 часа'),
            (4, '4 часа')
        ],
        initial=2,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    special_requests = forms.CharField(
        label='Особые пожелания',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Укажите дополнительные пожелания (аллергии, праздник, etc.)...'
        })
    )

    def __init__(self, *args, **kwargs):
        time_slots = kwargs.pop('time_slots', None)
        super().__init__(*args, **kwargs)

        if time_slots:
            self.fields['time'].choices = [('', 'Выберите время')] + [(t, t) for t in time_slots]

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.now().date():
            raise ValidationError('Нельзя выбрать прошедшую дату')
        return date


class TableSelectionForm(forms.Form):
    """Форма для выбора столика"""

    table = forms.ModelChoiceField(
        queryset=Table.objects.none(),
        widget=forms.HiddenInput(),
        empty_label=None
    )

    def __init__(self, *args, **kwargs):
        available_tables = kwargs.pop('available_tables', None)
        super().__init__(*args, **kwargs)

        if available_tables:
            self.fields['table'].queryset = available_tables
