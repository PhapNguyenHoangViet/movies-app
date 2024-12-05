from rest_framework import serializers
from core.models import (
    Movie,
    Tag,
    Rating,
    Genre,
    Chat,
)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['genre_id', 'genre_name']
        read_only_fields = ['genre_id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag_id', 'tag_name', 'created_at']
        read_only_fields = ['tag_id']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rating_id', 'rating', 'timestamp', 'processed']
        read_only_fields = ['rating_id']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['chat_id', 'question', 'answer', 'created']
        read_only_fields = ['chat_id']


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['movie_id', 'movie_title', 'release_date', 'image',
                  'genres', 'tags', 'ratings']
        read_only_fields = ['movie_id']

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


class MovieImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['movie_id', 'image']
        read_only_fields = ['movie_id']
        extra_kwargs = {'image': {'required': 'True'}}
