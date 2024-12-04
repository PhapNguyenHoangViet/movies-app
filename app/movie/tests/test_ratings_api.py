from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Rating
from core.models import Movie

from movie.serializers import RatingSerializer


RATINGS_URL = reverse('movie:rating-list')


def detail_url(rating_id):
    return reverse('movie:rating-detail', args=[rating_id])


def create_user(email='user@gmail.com', password='123456'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicratingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RATINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateratingsApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.movie = Movie.objects.create(
            movie_title='Sample Movie Title',
            release_date=None,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ratings(self):
        Rating.objects.create(user=self.user, movie=self.movie, rating=5)

        res = self.client.get(RATINGS_URL)

        ratings = Rating.objects.all()
        serializer = RatingSerializer(ratings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
