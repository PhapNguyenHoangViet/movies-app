from rest_framework import viewsets
from rest_framework import mixins

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Movie
from core.models import Tag
from core.models import Rating
from movie import serializers


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MovieDetailSerializer
    queryset = Movie.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MovieSerializer
        return self.serializer_class


class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(
            user=self.request.user).order_by('-tag_name')


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RatingSerializer
    queryset = Rating.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
