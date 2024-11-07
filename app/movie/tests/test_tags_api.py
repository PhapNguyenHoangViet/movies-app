from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Movie,
)

from movie.serializers import TagSerializer


TAGS_URL = reverse('movie:tag-list')


def detail_url(tag_id):
    return reverse('movie:tag-detail', args=[tag_id])


def create_user(email='user@gmail.com', password='123456'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, tag_name='Phap')
        Tag.objects.create(user=self.user, tag_name='Thuy')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-tag_name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        user2 = create_user(email='user2@gmail.com')
        Tag.objects.create(user=user2, tag_name='Phim hay')
        tag = Tag.objects.create(user=self.user, tag_name='Phim hai')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['tag_name'], tag.tag_name)
        self.assertEqual(res.data[0]['tag_id'], tag.tag_id)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, tag_name='Phim do')

        payload = {'tag_name': 'hay'}
        url = detail_url(tag.tag_id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.tag_name, payload['tag_name'])

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, tag_name='Hay')
        url = detail_url(tag.tag_id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_movies(self):
        tag1 = Tag.objects.create(user=self.user, tag_name='Hay')
        tag2 = Tag.objects.create(user=self.user, tag_name='0 Hay')
        movie = Movie.objects.create(movie_title='Superman')
        movie.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        tag = Tag.objects.create(user=self.user, tag_name='Hay')
        Tag.objects.create(user=self.user, tag_name='0 Hay')
        movie1 = Movie.objects.create(
            movie_title='Superman'
        )
        movie2 = Movie.objects.create(
            movie_title='Superman2'
        )
        movie1.tags.add(tag)
        movie2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
