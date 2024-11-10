from django.db.models.signals import post_save
from django.db.models import Avg
from .models import Rating


def update_movie_ratings(sender, instance, **kwargs):
    movie = instance.movie

    ratings = Rating.objects.filter(movie=movie)
    count = ratings.count()
    avg = ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0

    movie.count_rating = count
    movie.avg_rating = round(avg, 2)
    movie.save()


post_save.connect(update_movie_ratings, sender=Rating)
