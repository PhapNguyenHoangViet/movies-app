from rest_framework import viewsets

from core.models import Movie
from movie import serializers


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MovieDetailSerializer
    queryset = Movie.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MovieSerializer
        return self.serializer_class
