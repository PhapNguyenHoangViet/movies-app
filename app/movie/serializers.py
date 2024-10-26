"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Movie
        fields = ['id', 'movie_title', 'release_date', 'IMDb_URL', 'genre']
        read_only_fields = ['id']
