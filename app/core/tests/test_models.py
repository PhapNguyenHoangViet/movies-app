from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def create_user(email='user@gmail.com', password='123456'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""
    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@gmail.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@gmail.com', 'test1@gmail.com'],
            ['Test2@gmail.com', 'Test2@gmail.com'],
            ['TEST3@gmail.com', 'TEST3@gmail.com'],
            ['test4@gmail.COM', 'test4@gmail.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_movie(self):
        movie = models.Movie.objects.create(
            movie_title='Sample Movie Title',
            video_release_date=None,
            release_date=None,
            IMDb_URL='https://sample-movie.com',
            genre='action',
        )
        self.assertEqual(str(movie), movie.movie_title)

    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, tag_name='Tag1')

        self.assertEqual(str(tag), tag.tag_name)