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

app_name = 'movie'

urlpatterns = [
    path('', include(router.urls)),
]
