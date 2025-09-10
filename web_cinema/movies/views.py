from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from movies.models import Genre, Movie, Review, UserPreferences
from movies.utils import get_new_movies, get_recommendations, get_trending_movies
from movies.utils import get_similar_movies


def home(request):
    """Главная страница"""
    popular_movies = (
        Movie.objects.annotate(like_count=Count("liked_by"))
        .filter(like_count__gte=1)
        .order_by("-like_count")[:8]
    )

    new_movies = Movie.objects.order_by("-year")[:6]

    return render(
        request,
        "movies/home.html",
        {"popular_movies": popular_movies, "new_movies": new_movies},
    )


def movie_list(request):
    """Список всех фильмов"""
    movies = Movie.objects.all()
    genres = Genre.objects.all()

    # Фильтрация
    genre_filter = request.GET.get("genre")
    year_filter = request.GET.get("year")
    country_filter = request.GET.get("country")

    if genre_filter:
        movies = movies.filter(genres__name=genre_filter)
    if year_filter:
        movies = movies.filter(year=year_filter)
    if country_filter:
        movies = movies.filter(country__icontains=country_filter)

    return render(
        request, "movies/movie_list.html", {"movies": movies, "genres": genres}
    )

def movie_detail(request, movie_id):
    """Детальная страница фильма"""
    movie = get_object_or_404(Movie, id=movie_id)
    user_review = None
    user_liked = False
    user_disliked = False

    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(user=request.user, movie=movie)
        except Review.DoesNotExist:
            pass

        # Проверяем, лайкнул ли пользователь фильм
        try:
            prefs = UserPreferences.objects.get(user=request.user)
            user_liked = prefs.liked_movies.filter(id=movie.id).exists()
            user_disliked = prefs.disliked_movies.filter(id=movie.id).exists()
        except UserPreferences.DoesNotExist:
            pass

    # Статистика фильма
    like_count = movie.liked_by.count()
    dislike_count = movie.disliked_by.count()

    # Все отзывы к фильму
    reviews = (
        Review.objects.filter(movie=movie)
        .select_related("user")
        .order_by("-created_at")
    )

    # Похожие фильмы (используем улучшенный item-based подход)
    similar_movies = get_similar_movies(movie, request.user, limit=4)

    return render(
        request,
        "movies/movie_detail.html",
        {
            "movie": movie,
            "user_review": user_review,
            "user_liked": user_liked,
            "user_disliked": user_disliked,
            "like_count": like_count,
            "dislike_count": dislike_count,
            "reviews": reviews,
            "similar_movies": similar_movies,
        },
    )


@login_required
def add_review(request, movie_id):
    """Добавление отзыва"""
    if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        review_text = request.POST.get("review_text", "").strip()

        if not review_text:
            messages.error(request, "Отзыв не может быть пустым")
            return redirect("movies:movie_detail", movie_id=movie_id)

        if len(review_text) > 1000:
            messages.error(
                request, "Отзыв слишком длинный (максимум 1000 символов)"
            )
            return redirect("movies:movie_detail", movie_id=movie_id)

        # Создаем или обновляем отзыв
        review, created = Review.objects.get_or_create(
            user=request.user, movie=movie, defaults={"text": review_text}
        )

        if not created:
            review.text = review_text
            review.save()
            messages.success(request, "Отзыв обновлен!")
        else:
            messages.success(request, "Отзыв добавлен!")

        return redirect("movies:movie_detail", movie_id=movie_id)


@login_required
def rate_movie(request, movie_id):
    """Оценка фильма - лайк/дизлайк"""
    if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        action = request.POST.get("action")  # like или dislike

        # Получаем или создаем предпочтения пользователя
        prefs, created = UserPreferences.objects.get_or_create(
            user=request.user
        )

        if action == "like":
            prefs.liked_movies.add(movie)
            prefs.disliked_movies.remove(movie)
            messages.success(request, "Фильм добавлен в понравившиеся!")
        elif action == "dislike":
            prefs.disliked_movies.add(movie)
            prefs.liked_movies.remove(movie)
            messages.success(request, "Фильм добавлен в не понравившиеся!")
        elif action == "remove":
            prefs.liked_movies.remove(movie)
            prefs.disliked_movies.remove(movie)
            messages.success(request, "Оценка удалена!")

        return redirect("movies:movie_detail", movie_id=movie_id)


@login_required
def set_genre_preferences(request):
    """Выбор любимых жанров"""
    prefs, created = UserPreferences.objects.get_or_create(user=request.user)

    if request.method == "POST":
        genre_ids = request.POST.getlist("genres")
        prefs.favorite_genres.set(genre_ids)
        messages.success(request, "Ваши предпочтения сохранены!")
        return redirect(reverse("movies:recommendations"))

    genres = Genre.objects.all()
    return render(
        request,
        "movies/set_genre_preferences.html",
        {"genres": genres, "user_prefs": prefs},
    )


@login_required
def recommendations(request):
    """Персональные рекомендации"""
    try:
        UserPreferences.objects.get(user=request.user)
    except UserPreferences.DoesNotExist:
        messages.info(request, "Сначала выберите любимые жанры!")
        return redirect(reverse("movies:set_genre_preferences"))

    recommendations = get_recommendations(request.user, limit=12)
    new_movies = get_new_movies(6)
    trending_movies = get_trending_movies(4)

    return render(
        request,
        "movies/recommendations.html",
        {
            "recommendations": recommendations,
            "new_movies": new_movies,
            "trending_movies": trending_movies
        },
    )


def search(request):
    """Поиск фильмов"""
    query = request.GET.get("q", "")
    genre = request.GET.get("genre")
    year = request.GET.get("year")
    country = request.GET.get("country")

    movies = Movie.objects.all()

    if query:
        movies = movies.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if genre:
        movies = movies.filter(genres__name=genre)
    if year:
        movies = movies.filter(year=year)
    if country:
        movies = movies.filter(country__icontains=country)

    genres = Genre.objects.all()

    return render(
        request,
        "movies/search.html",
        {"movies": movies, "query": query, "genres": genres},
    )


@login_required
def my_ratings(request):
    """Мои оценки"""
    try:
        prefs = UserPreferences.objects.get(user=request.user)
        liked_movies = prefs.liked_movies.all()
        disliked_movies = prefs.disliked_movies.all()
    except UserPreferences.DoesNotExist:
        liked_movies = []
        disliked_movies = []

    return render(request, "movies/my_ratings.html", {
        "liked_movies": liked_movies,
        "disliked_movies": disliked_movies
    })