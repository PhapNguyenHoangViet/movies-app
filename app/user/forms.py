from core.models import User
from django import forms
from django.contrib.auth import get_user_model


class CustomUserCreationForm(forms.ModelForm):
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        label='Confirm Password'
    )
    dateOfBirth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
        label='Date of Birth'
    )
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    sex = forms.ChoiceField(
        choices=SEX_CHOICES,
        widget=forms.Select(attrs={'class': 'input'}),
        label='Sex',
        required=False
    )

    OCCUPATION_CHOICES = [
        ('student', 'Student'),
        ('technician', 'Technician'),
        ('administrator', 'Administrator'),
        ('writer', 'Writer'),
        ('executive', 'Executive'),
        ('lawyer', 'Lawyer'),
        ('educator', 'Educator'),
        ('scientist', 'Scientist'),
        ('entertainment', 'Entertainment'),
        ('programmer', 'Programmer'),
        ('librarian', 'Librarian'),
        ('homemaker', 'Homemaker'),
        ('artist', 'Artist'),
        ('engineer', 'Engineer'),
        ('marketing', 'Marketing'),
        ('healthcare', 'Healthcare'),
        ('retired', 'Retired'),
        ('salesman', 'Salesman'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
        ('none', 'None'),
    ]
    occupation = forms.ChoiceField(
        choices=OCCUPATION_CHOICES,
        widget=forms.Select(attrs={'class': 'input'}),
        label='Occupation',
        required=False
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm',
                  'name', 'dateOfBirth', 'sex', 'currentCity', 'occupation']
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


class ProfileForm(forms.ModelForm):
    dateOfBirth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
        label='Date of Birth'
    )
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    sex = forms.ChoiceField(
        choices=SEX_CHOICES,
        widget=forms.Select(attrs={'class': 'input'}),
        label='Sex',
        required=False
    )

    OCCUPATION_CHOICES = [
        ('student', 'Student'),
        ('technician', 'Technician'),
        ('administrator', 'Administrator'),
        ('writer', 'Writer'),
        ('executive', 'Executive'),
        ('lawyer', 'Lawyer'),
        ('educator', 'Educator'),
        ('scientist', 'Scientist'),
        ('entertainment', 'Entertainment'),
        ('programmer', 'Programmer'),
        ('librarian', 'Librarian'),
        ('homemaker', 'Homemaker'),
        ('artist', 'Artist'),
        ('engineer', 'Engineer'),
        ('marketing', 'Marketing'),
        ('healthcare', 'Healthcare'),
        ('retired', 'Retired'),
        ('salesman', 'Salesman'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
        ('none', 'None'),
    ]
    occupation = forms.ChoiceField(
        choices=OCCUPATION_CHOICES,
        widget=forms.Select(attrs={'class': 'input'}),
        label='Occupation',
        required=False
    )

    class Meta:
        model = User
        fields = ['email', 'name',
                  'dateOfBirth', 'sex', 'currentCity', 'occupation']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class ChangePasswordForm(forms.ModelForm):
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        label='Confirm Password')

    class Meta:
        model = User
        fields = ['password', 'password_confirm']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'input'}),
        }

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

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


class DeleteUserForm(forms.ModelForm):
    confirm_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input'}),
        label='Confirm Email'
    )

    class Meta:
        model = get_user_model()
        fields = []

    def __init__(self, *args, **kwargs):
        super(DeleteUserForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
