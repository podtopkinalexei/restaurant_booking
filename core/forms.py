from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Форма для добавления отзыва"""

    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐')
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        label='Ваша оценка'
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Поделитесь вашими впечатлениями о ресторане...',
                'class': 'form-control'
            }),
        }
        labels = {
            'comment': 'Ваш отзыв'
        }
