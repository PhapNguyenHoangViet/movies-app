from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, ProfileForm
from .forms import ChangePasswordForm, DeleteUserForm
from core.models import Genre

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)
from core.models import User
from .email_verification import EmailVerification
# from movie.gcn_model import MovieRecommender
# from django.conf import settings

# recommender = MovieRecommender(settings.MODEL_DIR)
# users, items, ratings, feature_matrix = recommender.prepare()


def log_in(request):
    if request.user.is_authenticated:
        return redirect('movie:home')

    if request.method == 'POST':
        email = request.POST['email'].lower()
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            
            # Check email verification
            if not user.is_email_verified:
                messages.warning(request, 'Please verify your email before logging in.')
                return redirect('user:log_in')
            
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET['next']
                                if 'next' in request.GET else 'movie:home')
            else:
                messages.error(request, 'Email or password is incorrect')
        except User.DoesNotExist:
            messages.error(request, 'Email does not exist')
    
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
            
            # Send verification email
            try:
                EmailVerification.send_verification_email(user, request)
                messages.success(request, 'Registration successful. Please check your email to verify your account.')
                return redirect('user:log_in')
            except Exception as e:
                # If email sending fails, delete the user and show error
                user.delete()
                messages.error(request, f'Error sending verification email: {str(e)}')
        else:
            messages.error(request, 'An error has occurred during registration')

    return render(request, 'sign_up.html', {"form": form})


def verify_email(request, token):
    is_valid, user = EmailVerification.verify_email_token(token)
    
    if is_valid:
        messages.success(request, 'Email verified successfully. You can now log in.')
    else:
        messages.error(request, 'Invalid or expired verification link.')
    
    return redirect('user:log_in')


@login_required(login_url='user:log_in')
def profile(request):
    top_5_genres = Genre.objects.all()[:5]
    profile = request.user
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user:profile')

    context = {'form': form, "genres": top_5_genres}
    return render(request, 'profile.html', context)


@login_required(login_url='user:log_in')
def delete(request):
    top_5_genres = Genre.objects.all()[:5]
    if request.method == 'POST':
        form = DeleteUserForm(request.POST, instance=request.user)
        if form.is_valid():
            confirm_email = form.cleaned_data['confirm_email'].lower()
            if confirm_email == request.user.email.lower():
                user = request.user
                user.delete()
                messages.success(request,
                                 "Your account has been successfully deleted.")
                return redirect('movie:welcome')
            else:
                messages.error(request, 'Email confirmation does not match.')
                return redirect('user:delete')
    else:
        form = DeleteUserForm(instance=request.user)

    context = {'form': form, "genres": top_5_genres}
    return render(request, 'delete_user.html', context)


@login_required(login_url='user:log_in')
def change_password(request):
    top_5_genres = Genre.objects.all()[:5]

    profile = request.user
    form = ChangePasswordForm(instance=profile)

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user:change_password')

    context = {'form': form, "genres": top_5_genres}
    return render(request, 'change_password.html', context)


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
