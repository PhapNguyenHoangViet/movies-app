from rest_framework import serializers
from core.models import Movie


class MovieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        fields = ['movie_id', 'movie_title', 'release_date',
                  'video_release_date', 'IMDb_URL', 'genre']
        read_only_fields = ['movie_id']

    def validate_genre(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Genre must be a list.")
        return value


class MovieDetailSerializer(MovieSerializer):
    class Meta(MovieSerializer.Meta):
        fields = MovieSerializer.Meta.fields
