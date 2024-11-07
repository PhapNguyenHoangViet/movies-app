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
    path('movie/', views.movie, name='movie'),
]
