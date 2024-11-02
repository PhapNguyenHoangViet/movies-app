from django.db import models
from django.conf import settings
from django.utils import timezone

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
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
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.movie_title


class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    rating = models.FloatField()
    timestamp = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'movie')

    def save(self, *args, **kwargs):
        existing_rating = Rating.objects.filter(
            user=self.user, movie=self.movie).first()
        if existing_rating:
            existing_rating.rating = self.rating
            existing_rating.timestamp = timezone.now()
            existing_rating.save()
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.user_id} rate {self.movie.movie_id}:{self.rating}"


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=255)
    created_at = models.DateField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.tag_name
