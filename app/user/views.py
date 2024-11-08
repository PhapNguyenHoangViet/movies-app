from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)
from core.models import User


def log_in(request):
    if request.user.is_authenticated:
        return redirect('movie:home')

    if request.method == 'POST':
        username = request.POST['email'].lower()
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Email does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'movie:home')
        else:
            messages.error(request, 'Email OR password is incorrect')
    return render(request, 'log_in.html')


def log_out(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('movie:welcome')


def sign_up(request):
    form = CustomUserCreationForm

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()
            messages.success(request, 'User account was created!')
            login(request, user)
            return redirect('user:log_in')

        else:
            messages.success(
                request, 'An error has occurred during registration')
            
    return render(request, 'sign_up.html', {
        "form":form,
    })


def profile(request):
    return render(request, 'profile.html')


def delete(request):
    return render(request, 'delete.html')


def change_password(request):
    return render(request, 'change_password.html')


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
