"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'


class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=1000)
    release_date = models.DateField(blank=True, null=True)
    video_release_date = models.DateField(blank=True, null=True)
    IMDb_URL = models.URLField(blank=True, null=True)
    genre = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.movie_title

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField()
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.email} rated {self.movie.movie_title} - {self.rating}'