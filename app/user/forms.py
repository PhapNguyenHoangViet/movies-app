from core.models import User
from django import forms

class CustomUserCreationForm(forms.ModelForm):
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        label='Confirm Password'
    )
    # Thêm trường Date of Birth và Sex
    dateOfBirth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
        label='Date of Birth'
    )
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    sex = forms.ChoiceField(
        choices=SEX_CHOICES,
        widget=forms.Select(attrs={'class': 'input'}),
        label='Sex',
        required=False
    )
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'name', 'dateOfBirth', 'sex', 'currentCity', 'occupation']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'input'}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user