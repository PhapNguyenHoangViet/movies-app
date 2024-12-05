import uuid
import os
from datetime import date

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def movie_image_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'movie', filename)


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
    user_id = models.IntegerField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    dateOfBirth = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    sex = models.CharField(max_length=10, null=True, blank=True)
    currentCity = models.CharField(max_length=255, null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    # Email verification fields
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(
        max_length=255, null=True, blank=True)
    email_verification_token_created_at = models.DateTimeField(
        null=True, blank=True)
    # Password reset fields
    password_reset_token = models.CharField(
        max_length=255, null=True, blank=True)
    password_reset_token_created_at = models.DateTimeField(
        null=True, blank=True)


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'

    def calculate_age(self):
        if self.dateOfBirth:
            today = date.today()
            age = today.year - self.dateOfBirth.year
            if today.month < self.dateOfBirth.month or (today.month == self.dateOfBirth.month and today.day < self.dateOfBirth.day):
                age -= 1
            return age
        return None
    
    def save(self, *args, **kwargs):
        if self.dateOfBirth:
            self.age = self.calculate_age()
        if not self.pk:
            if not self.user_id:
                max_id = User.objects.aggregate(models.Max('user_id'))['user_id__max']
                self.user_id = (max_id or 0) + 1
        super().save(*args, **kwargs)

class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=1000)
    release_date = models.DateField(blank=True, null=True)
    tags = models.ManyToManyField('Tag')
    genres = models.ManyToManyField('Genre')
    link_image = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(null=True, upload_to=movie_image_file_path)
    
    tmdb_id = models.PositiveIntegerField(blank=True, null=True)  # TMDb ID
    overview = models.TextField(blank=True, null=True)  # Overview
    runtime = models.PositiveIntegerField(blank=True, null=True)  # Runtime in minutes
    keywords = models.JSONField(blank=True, null=True)  # New model for keywords
    director = models.CharField(max_length=255, blank=True, null=True)  # Director name
    caster = models.JSONField(blank=True, null=True)  # Cast as text or linked to another model
    
    count_rating = models.PositiveIntegerField(default=0, blank=True, null=True)
    avg_rating = models.FloatField(default=0.0, blank=True, null=True)
    
    def __str__(self): return self.movie_title

    def update_rating(self):
        ratings = Rating.objects.filter(movie=self)
        total_ratings = ratings.count()
        if total_ratings > 0:
            self.avg_rating = round(sum(
                [rating.rating for rating in ratings]) / total_ratings, 1)
            self.count_rating = total_ratings
            self.save()


class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    timestamp = models.DateTimeField(blank=True, null=True)
    processed = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.user_id} rate {self.movie.movie_id}:{self.rating}"


class Genre(models.Model):
    genre_id = models.IntegerField(primary_key=True)
    genre_name = models.CharField(max_length=255)

    def __str__(self):
        return self.genre_name


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=255)
    created_at = models.DateField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag_name
    

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
