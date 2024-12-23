"""
URL mappings for the user API.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'user'

urlpatterns = [
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('profile/', views.profile, name='profile'),
    path('delete/', views.delete, name='delete'),
    path('change_password/', views.change_password, name='change_password'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),

    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_reset_confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
]
