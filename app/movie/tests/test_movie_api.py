import tempfile
import os
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Movie
from core.models import Tag

from movie.serializers import MovieSerializer
from movie.serializers import MovieDetailSerializer
from datetime import datetime

MOVIES_URL = reverse('movie:movie-list')


def detail_url(movie_id):
    return reverse('movie:movie-detail', args=[movie_id])


def image_upload_url(movie_id):
    return reverse('movie:movie-upload-image', args=[movie_id])


def create_user(email='user@gmail.com', password='123456'):
    return get_user_model().objects.create_user(email=email, password=password)


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


class MovieAPITests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

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
        movie = create_movie()

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
        self.assertFalse(Movie.objects.filter(
            movie_id=movie.movie_id).exists())

    def test_create_movie_with_new_tags(self):
        payload = {
            'movie_title': 'New movie title',
            'release_date': '2024-05-05',
            'video_release_date': '2024-05-05',
            'IMDb_URL': 'http://example.com/Newmovie.pdf',
            'genre': ['NewAction', 'NewDrama'],
            'tags': [{'tag_name': 'hay'}, {'tag_name': 'chua hay'}],
        }
        res = self.client.post(MOVIES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movies = Movie.objects.all()
        self.assertEqual(movies.count(), 1)
        movie = movies[0]
        self.assertEqual(movie.tags.count(), 2)
        for tag in payload['tags']:
            exists = movie.tags.filter(
                tag_name=tag['tag_name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_movie_with_existing_tags(self):
        tag_hay = Tag.objects.create(user=self.user, tag_name='hay')
        payload = {
            'movie_title': 'New movie title',
            'release_date': '2024-05-05',
            'video_release_date': '2024-05-05',
            'IMDb_URL': 'http://example.com/Newmovie.pdf',
            'genre': ['NewAction', 'NewDrama'],
            'tags': [{'tag_name': 'hay'}, {'tag_name': 'chua hay'}],
        }
        res = self.client.post(MOVIES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movies = Movie.objects.all()
        self.assertEqual(movies.count(), 1)
        movie = movies[0]
        self.assertEqual(movie.tags.count(), 2)
        self.assertIn(tag_hay, movie.tags.all())
        for tag in payload['tags']:
            exists = movie.tags.filter(
                tag_name=tag['tag_name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        movie = create_movie()

        payload = {'tags': [{'tag_name': 'Hay'}]}
        url = detail_url(movie.movie_id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, tag_name='Hay')
        self.assertIn(new_tag, movie.tags.all())

    def test_update_recipe_assign_tag(self):
        tag_hay = Tag.objects.create(user=self.user, tag_name='Hay')
        movie = create_movie()
        movie.tags.add(tag_hay)

        tag_khonghay = Tag.objects.create(user=self.user, tag_name='Khong hay')
        payload = {'tags': [{'tag_name': 'Khong hay'}]}
        url = detail_url(movie.movie_id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_khonghay, movie.tags.all())
        self.assertNotIn(tag_hay, movie.tags.all())

    def test_clear_movie_tags(self):
        tag = Tag.objects.create(user=self.user, tag_name='Hay')
        movie = create_movie()
        movie.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(movie.movie_id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(movie.tags.count(), 0)

    def test_filter_by_tags(self):
        r1 = create_movie(movie_title='Superman')
        r2 = create_movie(movie_title='Superman2')
        tag1 = Tag.objects.create(user=self.user, tag_name='Hay')
        tag2 = Tag.objects.create(user=self.user, tag_name='Không Hay')
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_movie(movie_title='Superman3')

        params = {'tags': f'{tag1.tag_id},{tag2.tag_id}'}
        res = self.client.get(MOVIES_URL, params)

        s1 = MovieSerializer(r1)
        s2 = MovieSerializer(r2)
        s3 = MovieSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.movie = create_movie()

    def tearDown(self):
        self.movie.image.delete()

    def test_upload_image(self):
        url = image_upload_url(self.movie.movie_id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.movie.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.movie.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.movie.movie_id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
