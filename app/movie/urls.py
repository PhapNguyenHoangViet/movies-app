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
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('all_genres/', views.all_genres, name='all_genres'),
    path('search/', views.movie_search, name='movie_search'),
    path('search-suggestions/', views.movie_search_suggestions, name='movie_search_suggestions'),
    path('filter_movies_by_genre/<str:genre>', views.filter_movies_by_genre, name='filter_movies_by_genre'),
    path('explore/<str:explore_name>', views.explore, name='explore'),
    path('about_your_ratings/', views.about_your_ratings, name='about_your_ratings'),
]
