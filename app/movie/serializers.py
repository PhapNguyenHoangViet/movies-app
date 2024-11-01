"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movies."""
    class Meta:
        model = Movie
        fields = ['movie_id', 'movie_title', 'release_date', 'video_release_date', 'IMDb_URL', 'genre']
        read_only_fields = ['movie_id']