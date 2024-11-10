from core.models import Rating
from django import forms


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-input'}),
        }
