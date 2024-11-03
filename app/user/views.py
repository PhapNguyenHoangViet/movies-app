from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from django.shortcuts import render

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


def welcome(request):
    return render(request, 'welcome.html')


def sign_up(request):
    return render(request, 'sign_up.html')


def log_in(request):
    return render(request, 'log_in.html')


def home(request):
    return render(request, 'home.html')


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
