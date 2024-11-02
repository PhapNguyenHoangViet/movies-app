from rest_framework import serializers
from core.models import (
    Movie,
    Tag,
    Rating,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag_id', 'tag_name', 'created_at']
        read_only_fields = ['tag_id']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rating_id', 'rating', 'timestamp']
        read_only_fields = ['rating_id']


class MovieSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['movie_id', 'movie_title', 'release_date',
                  'video_release_date', 'IMDb_URL', 'genre', 'tags', 'ratings']
        read_only_fields = ['movie_id']

    def validate_genre(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Genre must be a list.")
        return value

    def _get_or_create_tags(self, tags, movie):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            movie.tags.add(tag_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        movie = Movie.objects.create(**validated_data)
        self._get_or_create_tags(tags, movie)
        return movie

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class MovieDetailSerializer(MovieSerializer):
    class Meta(MovieSerializer.Meta):
        fields = MovieSerializer.Meta.fields
