from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Movie

from movie.serializers import MovieSerializer
from movie.serializers import MovieDetailSerializer
from datetime import datetime

MOVIES_URL = reverse('movie:movie-list')

def detail_url(movie_id):
    return reverse('movie:movie-detail', args=[movie_id])

def create_movie(**params):
    defaults = {
        'movie_title': 'Sample movie title',
        'release_date': '2024-05-05',
        'video_release_date': '2024-05-05',
        'IMDb_URL': 'http://example.com/movie.pdf',
        'genre': ['Action', 'Drama'],
    }
    defaults.update(params)

    movie = Movie.objects.create(**defaults)
    return movie


class PublicMovieAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(MOVIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_movies(self):
        create_movie()

        res = self.client.get(MOVIES_URL)

        movies = Movie.objects.all().order_by('-movie_id')
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_get_movie_detail(self):
        movie = create_movie()
        url = detail_url(movie.movie_id)
        res = self.client.get(url)

        serializer = MovieDetailSerializer(movie)
        self.assertEqual(res.data, serializer.data)

    def test_create_movie(self):
        payload = {
            'movie_title': 'Sample movie title',
            'release_date': '2024-05-05',
            'video_release_date': '2024-05-05',
            'IMDb_URL': 'http://example.com/movie.pdf',
            'genre': ['Action', 'Drama'],
        }
        res = self.client.post(MOVIES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movie = Movie.objects.get(movie_id=res.data['movie_id'])
        for k, v in payload.items():
            if k in ['release_date', 'video_release_date']:
                v = datetime.strptime(v, '%Y-%m-%d').date()
            self.assertEqual(getattr(movie, k), v)


    def test_partial_update(self):
        original_link = 'https://example.com/movie.pdf'
        movie = create_movie(
            movie_title='Sample movie title',
            IMDb_URL=original_link,
        )

        payload = {'movie_title': 'New movie title'}
        url = detail_url(movie.movie_id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        movie.refresh_from_db()
        self.assertEqual(movie.movie_title, payload['movie_title'])
        self.assertEqual(movie.IMDb_URL, original_link)

    def test_full_update(self):
        original_link = 'https://example.com/movie.pdf'
        movie = create_movie(
            movie_title='Sample movie title',
            IMDb_URL=original_link,
        )

        payload = {'movie_title': 'New movie title'}
        url = detail_url(movie.movie_id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        movie.refresh_from_db()
        self.assertEqual(movie.movie_title, payload['movie_title'])
        self.assertEqual(movie.IMDb_URL, original_link)


    def test_full_update(self):
        movie = create_movie(
        )

        payload = {
            'movie_title': 'New movie title',
            'release_date': '2024-05-05',
            'video_release_date': '2024-05-05',
            'IMDb_URL': 'http://example.com/Newmovie.pdf',
            'genre': ['NewAction', 'NewDrama'],
        }

        url = detail_url(movie.movie_id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        movie.refresh_from_db()
        for k, v in payload.items():
            if k in ['release_date', 'video_release_date']:
                v = datetime.strptime(v, '%Y-%m-%d').date()
            self.assertEqual(getattr(movie, k), v)

    def test_delete_movie(self):
        movie = create_movie()

        url = detail_url(movie.movie_id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Movie.objects.filter(movie_id=movie.movie_id).exists())