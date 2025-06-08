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
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    JsonResponse,
    StreamingHttpResponse,
)
from django.urls import reverse
from core.models import Movie, Tag, Rating, Genre, Comment, Chat
from movie import serializers
from django.db.models import Count
from django.db.models import F
from django.utils import timezone
from datetime import datetime
from .forms import CommentForm
from django.db.models import Case, When
from django.conf import settings
from django.db.models import Count, Avg
import json
from django.contrib import messages
import requests
import os

AI_MOVIE_API_URL = "https://39be-116-111-7-185.ngrok-free.app/themovie/api/v1"

@login_required(login_url="user:log_in")
def rate_movie(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    if request.user.is_authenticated:
        existing_rating = Rating.objects.filter(user=request.user, movie=movie).first()
        if existing_rating:
            existing_rating.rating = request.POST.get("rating")
            existing_rating.timestamp = timezone.now()
            existing_rating.save()
        else:
            rating = Rating(
                user=request.user,
                movie=movie,
                timestamp=timezone.now(),
                rating=request.POST.get("rating"),
            )
            rating.save()
        movie.update_rating()
        try:
            update_url = f"{AI_MOVIE_API_URL}/movie/update-model"
            response = requests.post(update_url, json={"epochs": 200})
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get("status") == "success":
                    messages.success(
                        request, resp_json.get("message", "Model updated successfully!")
                    )
                else:
                    messages.info(
                        request, resp_json.get("message", "Waiting for more ratings...")
                    )
            else:
                messages.warning(request, "Failed to update model.")
        except Exception as e:
            messages.error(request, f"Error updating model: {str(e)}")
        return redirect("movie:movie_detail", movie_id=movie_id)
    return redirect("user:log_in")


@csrf_exempt
def chatbot(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    data = json.loads(request.body)
    question = data.get("question", "")
    if not question:
        return JsonResponse({"error": "No question provided"}, status=400)

    chats = Chat.objects.filter(user=request.user).order_by("-created_at")[:20]
    chat_history = [
        {"question": chat.question, "answer": chat.answer} for chat in chats
    ]
    context = ""
    if chat_history:
        context = "=== LỊCH SỬ HỘI THOẠI GẦN ĐÂY ===\n"
        for i, chat in enumerate(chat_history, 1):
            context += f"Hội thoại {i}:\n"
            context += f"Câu hỏi: {chat['question']}\n"
            context += f"Trả lời: {chat['answer']}\n\n"
        context += "=== KẾT THÚC LỊCH SỬ ===\n\n"

    # Tạo prompt chính
    prompt = f"""{context}Bạn là một trợ lý AI thông minh và hữu ích. 

    HƯỚNG DẪN:
    1. Đọc kỹ lịch sử hội thoại bên trên để hiểu ngữ cảnh
    2. Sử dụng thông tin từ lịch sử nếu có liên quan đến câu hỏi hiện tại
    3. Nếu lịch sử không liên quan, hãy bỏ qua và trả lời trực tiếp câu hỏi
    4. Trả lời bằng ngôn ngữ mà người dùng sử dụng trong câu hỏi
    5. Cung cấp câu trả lời chi tiết, chính xác và hữu ích

    CÂUHỎI CỦA NGƯỜI DÙNG: {question}

    Hãy trả lời câu hỏi trên một cách tự nhiên và hữu ích."""
    # Biến để lưu trữ toàn bộ câu trả lời
    complete_answer = ""
    save_attempted = False

    def stream_response():
        nonlocal complete_answer, save_attempted
        try:
            chat_url = f"{AI_MOVIE_API_URL}/conversation/chat"

            with requests.post(
                chat_url,
                headers={"Content-Type": "application/json"},
                json={
                    "conversation_id": "857e0395-eb1e-4001-ac4d-f4fffbddb3c4",
                    "user_id": str(request.user.user_id),
                    "message": prompt,
                },
                stream=True,
                timeout=(30, 300),  # 30s connection, 300s read timeout
            ) as r:
                if r.status_code != 200:
                    yield 'data: {"error": "failed to stream from AI API"}\n\n'
                    return

                try:
                    for chunk in r.iter_lines(decode_unicode=True):
                        if chunk:

                            # Kiểm tra xem chunk có bắt đầu bằng "data: " không
                            if chunk.startswith("data: "):
                                json_part = chunk[6:]  # Bỏ "data: " ở đầu

                                try:
                                    # Parse JSON từ phần sau "data: "
                                    chunk_data = json.loads(json_part)

                                    if chunk_data.get(
                                        "status"
                                    ) == "success" and chunk_data.get("data"):
                                        message = chunk_data["data"].get("message", "")
                                        msg_type = chunk_data["data"].get("type", "")
                                        # Chỉ lưu message từ AI và không phải là [END]
                                        if (
                                            msg_type == "ai"
                                            and message
                                            and message != "[END]"
                                        ):
                                            complete_answer += message

                                        # Nếu gặp [END] thì lưu vào database
                                        elif message == "[END]" and not save_attempted:
                                            save_attempted = True
                                            try:
                                                user = (
                                                    request.user
                                                    if request.user.is_authenticated
                                                    else None
                                                )
                                                print(f"[DEBUG] User: {user}")

                                                if (
                                                    complete_answer.strip()
                                                ):  # Chỉ save khi có nội dung
                                                    chat_obj = Chat.objects.create(
                                                        question=question,
                                                        answer=complete_answer.strip(),
                                                        user=user,
                                                        created_at=timezone.now(),
                                                    )
                                                else:
                                                    print("[DEBUG] No content to save")

                                            except Exception as save_error:
                                                print(
                                                    f"[ERROR] Error saving chat: {save_error}"
                                                )
                                                import traceback

                                                traceback.print_exc()

                                except json.JSONDecodeError as json_error:
                                    print(
                                        f"[DEBUG] JSON decode error for: '{json_part}' - {json_error}"
                                    )

                            # Chuyển tiếp chunk gốc tới frontend
                            yield f"{chunk}\n\n"

                except requests.exceptions.ChunkedEncodingError as chunk_error:
                    print(f"[ERROR] Chunked encoding error: {chunk_error}")
                    # Vẫn cố gắng lưu nếu có dữ liệu
                    if complete_answer.strip() and not save_attempted:
                        try:
                            user = (
                                request.user if request.user.is_authenticated else None
                            )
                            chat_obj = Chat.objects.create(
                                question=question,
                                answer=complete_answer.strip(),
                                user=user,
                                created_at=timezone.now(),
                            )
                        except Exception as emergency_save_error:
                            print(
                                f"[ERROR] Emergency save failed: {emergency_save_error}"
                            )

        except requests.exceptions.RequestException as req_error:
            print(f"[ERROR] Request exception: {req_error}")
            yield f'data: {{"error": "Request failed: {str(req_error)}"}}\n\n'

        except Exception as e:
            print(f"[ERROR] Stream exception: {e}")
            import traceback

            traceback.print_exc()
            yield f'data: {{"error": "{str(e)}"}}\n\n'

        finally:
            print(f"[DEBUG] Stream ended. Final answer length: {len(complete_answer)}")
            print(f"[DEBUG] Save attempted: {save_attempted}")

            # Fallback save nếu chưa lưu được và có nội dung
            if complete_answer.strip() and not save_attempted:
                print("[DEBUG] Attempting fallback save...")
                try:
                    user = request.user if request.user.is_authenticated else None
                    chat_obj = Chat.objects.create(
                        question=question,
                        answer=complete_answer.strip(),
                        user=user,
                        created_at=timezone.now(),
                    )
                except Exception as fallback_error:
                    print(f"[ERROR] Fallback save failed: {fallback_error}")

    return StreamingHttpResponse(stream_response(), content_type="text/event-stream")


@login_required
def get_chat_history(request):
    chats = Chat.objects.filter(user=request.user).order_by("-created_at")[:5]
    chat_data = [{"question": chat.question, "answer": chat.answer} for chat in chats]
    return JsonResponse({"history": chat_data})


def home(request):
    user = request.user
    if user.is_authenticated:
        user_ratings_count = Rating.objects.filter(user=user).count()
        if user_ratings_count >= 5:
            try:
                rec_url = f"{AI_MOVIE_API_URL}/movie/recommendations/{user.user_id}"
                response = requests.get(rec_url, params={"top_k": 21})
                if response.status_code == 200:
                    resp_json = response.json()
                    if resp_json.get("status") == "success":
                        recommendations = resp_json["data"]["recommendations"]

                        movie_ids = [movie_id for movie_id, _ in recommendations]
                        # rated_movie_ids = Rating.objects.filter(user=user).values_list(
                        #     "movie__movie_id", flat=True
                        # )
                        # movie_ids = [
                        #     movie_id
                        #     for movie_id, _ in recommendations
                        #     if movie_id not in rated_movie_ids
                        # ]

                        ordering = Case(
                            *[
                                When(movie_id=movie_id, then=index)
                                for index, movie_id in enumerate(movie_ids)
                            ]
                        )
                        top_picks = Movie.objects.filter(
                            movie_id__in=movie_ids
                        ).order_by(ordering)
                    else:
                        # messages.info(request, "Không có gợi ý phù hợp.")
                        top_picks = Movie.objects.filter(
                            release_date__lte=datetime.now(), avg_rating__gte=4.0
                        ).order_by("-release_date", "-avg_rating")[:20]
                else:
                    messages.warning(request, "Không thể lấy gợi ý phim.")
                    top_picks = Movie.objects.filter(
                        release_date__lte=datetime.now(), avg_rating__gte=4.0
                    ).order_by("-release_date", "-avg_rating")[:20]
            except Exception as e:
                messages.error(request, f"Lỗi khi lấy gợi ý phim: {str(e)}")
                top_picks = Movie.objects.filter(
                    release_date__lte=datetime.now(), avg_rating__gte=4.0
                ).order_by("-release_date", "-avg_rating")[:20]
        else:
            top_picks = Movie.objects.filter(
                release_date__lte=datetime.now(), avg_rating__gte=4.0
            ).order_by("-release_date", "-avg_rating")[:20]

    else:
        top_picks = Movie.objects.filter(
            release_date__lte=datetime.now(), avg_rating__gte=4.0
        ).order_by("-release_date", "-avg_rating")[:20]

    recent_movies = (
        Movie.objects.all()
        .filter(release_date__lte=datetime.now())
        .order_by("-release_date")[:20]
    )
    count_rating_movies = Movie.objects.all().order_by("-count_rating")[:20]
    avg_rating_movies = Movie.objects.all().order_by("-avg_rating")[:20]

    top_5_genres = Genre.objects.all()[:5]

    return render(
        request,
        "home.html",
        {
            "top_picks": top_picks,
            "recent_movies": recent_movies,
            "count_rating_movies": count_rating_movies,
            "avg_rating_movies": avg_rating_movies,
            "genres": top_5_genres,
        },
    )


@login_required(login_url="user:log_in")
def recommendations(request):
    user = request.user
    recommendations = []

    rec_url = f"{AI_MOVIE_API_URL}/movie/recommendations/{user.user_id}"
    response = requests.get(rec_url, params={"top_k": 100})
    if response.status_code == 200:
        resp_json = response.json()
        if resp_json.get("status") == "success":
            recommendations = resp_json["data"]["recommendations"]
    rated_movie_ids = Rating.objects.filter(user=user).values_list(
        "movie__movie_id", flat=True
    )
    movie_ids = [
        movie_id for movie_id, _ in recommendations if movie_id not in rated_movie_ids
    ]

    ordering = Case(
        *[
            When(movie_id=movie_id, then=index)
            for index, movie_id in enumerate(movie_ids)
        ]
    )
    top_picks = Movie.objects.filter(movie_id__in=movie_ids).order_by(ordering)
    recommendations_data = [
        {
            "movie_id": movie.movie_id,
            "movie_title": movie.movie_title,
            "avg_rating": movie.avg_rating,
        }
        for movie in top_picks
    ]
    return JsonResponse(
        {"recommendations": recommendations_data}, safe=False, status=200
    )


def movie_detail(request, movie_id):
    top_5_genres = Genre.objects.all()[:5]
    movie = get_object_or_404(Movie, movie_id=movie_id)
    movie_genres = Genre.objects.filter(movie=movie)

    user_rating = None
    commentForm = CommentForm()
    comments = Comment.objects.filter(movie=movie, parent=None).order_by("-date")
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, movie=movie).first()
        if request.POST:
            cmtForm = CommentForm(request.POST)
            if cmtForm.is_valid():
                parent_obj = None
                if request.POST.get("parent"):
                    parent = request.POST.get("parent")
                    parent_obj = Comment.objects.get(comment_id=parent)
                    if parent_obj:
                        comment_reply = cmtForm.save(commit=False)
                        comment_reply.parent = parent_obj
                        comment_reply.movie = movie
                        comment_reply.user = request.user
                        comment_reply.save()
                        return HttpResponseRedirect(
                            reverse("movie:movie_detail", kwargs={"movie_id": movie_id})
                        )

                else:
                    comment = cmtForm.save(commit=False)
                    comment.movie = movie
                    comment.user = request.user
                    comment.save()
                    return HttpResponseRedirect(
                        reverse("movie:movie_detail", kwargs={"movie_id": movie_id})
                    )

    return render(
        request,
        "movie_detail.html",
        {
            "movie": movie,
            "movie_genres": movie_genres,
            "user_rating": user_rating,
            "genres": top_5_genres,
            "commentForm": commentForm,
            "comments": comments,
        },
    )


@login_required(login_url="user:log_in")
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)
    if request.user == comment.user or request.user == comment.parent.user:
        comment.delete()
        return redirect(
            "movie:movie_detail", movie_id=comment.movie.movie_id
        )  # redirect về trang chi tiết phim
    else:
        return HttpResponse(
            "You are not authorized to delete this comment.", status=403
        )


@login_required(login_url="user:log_in")
def explore(request, explore_name):
    user = request.user
    top_5_genres = Genre.objects.all()[:5]
    movies = []
    content = ""
    sort = request.GET.get("sort", "default")
    order = request.GET.get("order", "desc")

    if explore_name == "top_picks":
        content = "Top picks"
        recommendations = []
        rec_url = f"{AI_MOVIE_API_URL}/movie/recommendations/{user.user_id}"
        response = requests.get(rec_url, params={"top_k": 100})
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("status") == "success":
                recommendations = resp_json["data"]["recommendations"]
        movie_ids = [movie_id for movie_id, _ in recommendations]
        ordering = Case(
            *[
                When(movie_id=movie_id, then=index)
                for index, movie_id in enumerate(movie_ids)
            ]
        )
        movies = Movie.objects.filter(movie_id__in=movie_ids).order_by(ordering)
    elif explore_name == "recent_movies":
        movies = Movie.objects.filter(release_date__lte=datetime.now()).order_by(
            "-release_date"
        )
        content = "Recent movies"
    elif explore_name == "count_rating_movies":
        movies = Movie.objects.all().order_by("-count_rating")
        content = "Rating more"
    elif explore_name == "avg_rating_movies":
        movies = Movie.objects.all().order_by("-avg_rating")
        content = "Favorite Movies"
    elif explore_name == "ratings":
        movies = Movie.objects.filter(rating__user=user).distinct()
        content = "Movies you've rated"

    if sort == "release_date":
        movies = movies.order_by(
            F("release_date").desc() if order == "desc" else F("release_date").asc()
        )
    elif sort == "count_rating":
        movies = movies.order_by(
            F("count_rating").desc() if order == "desc" else F("count_rating").asc()
        )
    elif sort == "avg_rating":
        movies = movies.order_by(
            F("avg_rating").desc() if order == "desc" else F("avg_rating").asc()
        )

    paginator = Paginator(movies, 21)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    visible_pages = get_visible_page_numbers(page_obj.number, paginator.num_pages)

    return render(
        request,
        "explore.html",
        {
            "page_obj": page_obj,
            "movies": movies,
            "genres": top_5_genres,
            "content": content,
            "visible_pages": visible_pages,
            "current_sort": sort,
            "current_order": order,
        },
    )


@login_required(login_url="user:log_in")
def about_your_ratings(request):
    user = request.user
    user_ratings = Rating.objects.filter(user=request.user)
    rated_movies = user.rating_set.all()  # Giả sử bạn có quan hệ "rating_set" cho User
    total_rated_movies = rated_movies.count()

    top_5_genres = Genre.objects.all()[:5]
    # Prepare data for charts
    rating_distribution = list(
        user_ratings.values("rating")
        .annotate(frequency=Count("rating"))
        .order_by("rating")
    )
    ratings_over_time = list(
        user_ratings.order_by("timestamp")
        .values("timestamp__month", "timestamp__year")
        .annotate(num_ratings=Count("rating"))
        .order_by("timestamp__year", "timestamp__month")
    )
    release_years = list(
        user_ratings.values("movie__release_date__year")
        .annotate(num_movies=Count("movie__release_date__year"))
        .order_by("movie__release_date__year")
    )
    genre_ratings = list(
        user_ratings.values("movie__genres__genre_name")
        .annotate(num_movies=Count("movie__genres__genre_name"))
        .order_by("-num_movies")
    )
    avg_ratings_by_genre = list(
        user_ratings.values("movie__genres__genre_name")
        .annotate(avg_rating=Avg("rating"))
        .order_by("movie__genres__genre_name")
    )
    context = {
        "genres": top_5_genres,
        "total_rated_movies": total_rated_movies,
        "rating_distribution": json.dumps(rating_distribution),
        "ratings_over_time": json.dumps(ratings_over_time),
        "release_years": json.dumps(release_years),
        "genre_ratings": json.dumps(genre_ratings),
        "avg_ratings_by_genre": json.dumps(avg_ratings_by_genre),
    }

    return render(request, "about_your_ratings.html", context)


def movie_search(request):
    top_5_genres = Genre.objects.all()[:5]
    query = request.GET.get("q", "")
    movies = Movie.objects.filter(movie_title__icontains=query)

    paginator = Paginator(movies, 21)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    visible_pages = get_visible_page_numbers(page_obj.number, paginator.num_pages)

    return render(
        request,
        "movie_search.html",
        {
            "page_obj": page_obj,
            "visible_pages": visible_pages,
            "movies": movies,
            "query": query,
            "genres": top_5_genres,
        },
    )


def movie_search_suggestions(request):
    query = request.GET.get("q", "")
    if query:
        suggestions = Movie.objects.filter(movie_title__icontains=query).values(
            "movie_title"
        )[:10]
        movie_titles = [suggestion["movie_title"] for suggestion in suggestions]
        return JsonResponse({"suggestions": movie_titles})
    return JsonResponse({"suggestions": []})


def filter_movies_by_genre(request, genre):
    movies = Movie.objects.filter(genres__genre_name=genre)
    top_5_genres = Genre.objects.all()[:5]
    query = genre

    paginator = Paginator(movies, 21)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    visible_pages = get_visible_page_numbers(page_obj.number, paginator.num_pages)

    return render(
        request,
        "movie_search.html",
        {
            "page_obj": page_obj,
            "visible_pages": visible_pages,
            "movies": movies,
            "query": query,
            "genres": top_5_genres,
        },
    )


def all_genres(request):
    top_5_genres = Genre.objects.all()[:5]
    genres = Genre.objects.annotate(num_movies=Count("movie")).order_by("-num_movies")
    return render(
        request, "all_genres.html", {"all_genres": genres, "genres": top_5_genres}
    )


def get_visible_page_numbers(current_page, total_pages, delta=2):
    pages = {1, total_pages}

    start = max(current_page - delta, 1)
    end = min(current_page + delta, total_pages)
    pages.update(range(start, end + 1))
    return sorted(pages)


def welcome(request):
    return render(request, "welcome.html")


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="Comma separated list of tag IDs to filter",
            ),
        ]
    )
)
class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MovieDetailSerializer
    queryset = Movie.objects.all()

    def _params_to_ints(self, qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        tags = self.request.query_params.get("tags")
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__tag_id__in=tag_ids)
        return queryset.order_by("-movie_id").distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.MovieSerializer
        elif self.action == "upload_image":
            return serializers.MovieImageSerializer
        return self.serializer_class

    @action(methods=["POST"], detail=True, url_path="upload-image")
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
                "assigned_only",
                OpenApiTypes.INT,
                enum=[0, 1],
            ),
        ]
    )
)
class TagViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get("assigned_only", 0)))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(movie__isnull=False)

        return queryset.filter(user=self.request.user).order_by("-tag_name").distinct()


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
