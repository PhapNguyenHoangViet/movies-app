from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from core.models import Movie, Tag, Rating, Genre, Comment
from movie import serializers
from django.db.models import Count
from django.utils import timezone
from datetime import datetime
from .forms import CommentForm
from .gcn_model import recommend_movies



@login_required(login_url='user:log_in')
def rate_movie(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    if request.user.is_authenticated:
        existing_rating = Rating.objects.filter(
            user=request.user, movie=movie).first()
        if existing_rating:
            existing_rating.rating = request.POST.get('rating')
            existing_rating.timestamp = timezone.now()
            existing_rating.save()
        else:
            rating = Rating(
                user=request.user,
                movie=movie,
                timestamp=timezone.now(),
                rating=request.POST.get('rating')
            )
            rating.save()
        movie.update_rating()
        return redirect('movie:movie_detail', movie_id=movie_id)
    return redirect('user:log_in')


def home(request):
    user = request.user
    movie_ids = recommend_movies(user.user_id, 1682)
    top_picks = Movie.objects.filter(movie_id__in=movie_ids).order_by('-avg_rating')[:20]
    recent_movies = Movie.objects.all().filter(
        release_date__lte=datetime.now()).order_by('-release_date')[:20]
    count_rating_movies = Movie.objects.all().order_by('-count_rating')[:20]
    avg_rating_movies = Movie.objects.all().order_by('-avg_rating')[:20]

    top_5_genres = Genre.objects.all()[:5]

    return render(request, 'home.html', {
        "top_picks": top_picks,
        "recent_movies": recent_movies,
        "count_rating_movies": count_rating_movies,
        "avg_rating_movies": avg_rating_movies,
        "genres": top_5_genres,
        })


def movie_detail(request, movie_id):
    top_5_genres = Genre.objects.all()[:5]
    movie = get_object_or_404(Movie, movie_id=movie_id)
    movie_genres = Genre.objects.filter(movie=movie)

    user_rating = None
    commentForm = CommentForm()
    comments = Comment.objects.filter(movie=movie, parent=None).order_by('-date')
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(
            user=request.user, movie=movie).first()
        if request.POST:
            cmtForm = CommentForm(request.POST)
            if cmtForm.is_valid:
                parent_obj = None
                if request.POST.get('parent'):
                    parent = request.POST.get('parent')
                    parent_obj = Comment.objects.get(comment_id=parent)
                    if parent_obj:
                        comment_reply = cmtForm.save(commit=False)
                        comment_reply.parent = parent_obj
                        comment_reply.movie = movie
                        comment_reply.user=request.user
                        comment_reply.save()
                        return HttpResponseRedirect(reverse('movie:movie_detail', kwargs={'movie_id':movie_id}))

                else: 
                    comment = cmtForm.save(commit=False)
                    comment.movie = movie
                    comment.user=request.user
                    comment.save()
                    return HttpResponseRedirect(reverse('movie:movie_detail', kwargs={'movie_id':movie_id}))

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'movie_genres': movie_genres,
        'user_rating': user_rating,
        'genres': top_5_genres,
        'commentForm': commentForm,
        'comments':comments,
    })


@login_required(login_url='user:log_in')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)
    if request.user == comment.user or request.user == comment.parent.user:
        comment.delete()
        return redirect('movie:movie_detail', movie_id=comment.movie.movie_id)  # redirect về trang chi tiết phim
    else:
        return HttpResponse("You are not authorized to delete this comment.", status=403)


def welcome(request):
    return render(request, 'welcome.html')


@login_required(login_url='user:log_in')
def explore(request, explore_name):
    user = request.user
    top_5_genres = Genre.objects.all()[:5]
    movies = []
    if (explore_name == 'top_picks'):
        movie_ids = recommend_movies(user.user_id, 1682)
        movies = Movie.objects.filter(movie_id__in=movie_ids).order_by('-avg_rating')[:20]
        content = 'Top picks'
    elif (explore_name == 'recent_movies'):
        movies = Movie.objects.all().filter(
        release_date__lte=datetime.now()).order_by('-release_date')
        content = 'Recent movies'
    elif (explore_name == 'count_rating_movies'):
        movies = Movie.objects.all().order_by('-count_rating')
        content = 'Rating more'
    elif (explore_name == 'avg_rating_movies'):
        movies = Movie.objects.all().order_by('-avg_rating')
        content = 'Favorite Movies'
    elif (explore_name == 'ratings'):
        movies = Movie.objects.filter(rating__user=user).distinct()
        content = "Movies you've rated"

    paginator = Paginator(movies, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'explore.html', {
        'page_obj': page_obj, 
        'movies': movies,
        'genres': top_5_genres,
        'content':content,
    })


@login_required(login_url='user:log_in')
def about_your_ratings(request):
    return render(request, 'about_your_ratings.html', {
    })

def movie_search(request):
    top_5_genres = Genre.objects.all()[:5]
    query = request.GET.get('q', '')
    movies = Movie.objects.filter(movie_title__icontains=query)

    return render(request, 'movie_search.html', {
        'movies': movies,
        'query': query,
        'genres': top_5_genres,
    })


def movie_search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        suggestions = Movie.objects.filter(movie_title__icontains=query).values('movie_title')[:10]
        movie_titles = [suggestion['movie_title'] for suggestion in suggestions]
        return JsonResponse({'suggestions': movie_titles})
    return JsonResponse({'suggestions': []})



def filter_movies_by_genre(request, genre):
    movies = Movie.objects.filter(genres__genre_name=genre)
    top_5_genres = Genre.objects.all()[:5]
    query = genre
    return render(request, 'movie_search.html', {'movies': movies, 'genres': top_5_genres, 'query': query})


def all_genres(request):
    top_5_genres = Genre.objects.all()[:5]
    genres = Genre.objects.annotate(num_movies=Count('movie')).order_by('-num_movies')
    return render(request, 'all_genres.html', {'all_genres': genres, 'genres': top_5_genres })


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
        ]
    )
)
class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MovieDetailSerializer
    queryset = Movie.objects.all()

    def _params_to_ints(self, qs):
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        tags = self.request.query_params.get('tags')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__tag_id__in=tag_ids)
        return queryset.order_by('-movie_id').distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MovieSerializer
        elif self.action == 'upload_image':
            return serializers.MovieImageSerializer
        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
            ),
        ]
    )
)
class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(movie__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-tag_name').distinct()


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RatingSerializer
    queryset = Rating.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GenreSerializer
    queryset = Genre.objects.all()
