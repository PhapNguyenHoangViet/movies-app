from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Movie
from movie import serializers


class MovieViewSet(viewsets.ModelViewSet):
    """View for manage Movie APIs."""
    serializer_class = serializers.MovieSerializer
    queryset = Movie.objects.all()
