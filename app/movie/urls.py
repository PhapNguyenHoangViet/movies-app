from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from movie import views


router = DefaultRouter()
router.register('movies', views.MovieViewSet)
router.register('tags', views.TagViewSet)
router.register('ratings', views.RatingViewSet)
router.register('genres', views.GenreViewSet)

app_name = 'movie'

urlpatterns = [
    path('', include(router.urls)),
    path('home/', views.home, name='home'),
    path('welcome/', views.welcome, name='welcome'),
    path('movie_detail/<int:movie_id>/',
         views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/rate/', views.rate_movie, name='rate_movie'),
]
