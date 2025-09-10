import random
from django.db.models import Count, Q, Avg
from movies.models import Movie, UserPreferences, Genre, Review
from django.contrib.auth.models import User


def get_recommendations(user, limit=10):
    """
    Простая система рекомендаций на основе любимых жанров
    """
    try:
        prefs = UserPreferences.objects.get(user=user)
    except UserPreferences.DoesNotExist:
        return get_popular_movies(limit)

    # Фильмы в любимых жанрах пользователя
    genre_movies = Movie.objects.filter(genres__in=prefs.favorite_genres.all())

    # Исключаем уже оцененные фильмы
    try:
        user_prefs = UserPreferences.objects.get(user=user)
        rated_movies = list(user_prefs.liked_movies.values_list('id', flat=True)) + \
                       list(user_prefs.disliked_movies.values_list('id', flat=True))
        genre_movies = genre_movies.exclude(id__in=rated_movies)
    except UserPreferences.DoesNotExist:
        pass

    # Если мало рекомендаций - добавляем популярные
    if genre_movies.count() < limit:
        popular = get_popular_movies(limit - genre_movies.count())
        recommendations = list(genre_movies) + list(popular)
    else:
        recommendations = list(genre_movies)

    # Перемешиваем для разнообразия
    random.shuffle(recommendations)
    return recommendations[:limit]


def get_popular_movies(limit=10):
    """Самые популярные фильмы по лайкам"""
    return Movie.objects.annotate(
        like_count=Count('liked_by')
    ).filter(like_count__gte=1).order_by('-like_count')[:limit]


def calculate_item_similarity(movie1, movie2):
    """
    Вычисляет схожесть между двумя фильмами
    на основе оценок пользователей
    """
    # Пользователи, которые оценили оба фильма
    users_movie1 = set(UserPreferences.objects.filter(
        Q(liked_movies=movie1) | Q(disliked_movies=movie1)
    ).values_list('user_id', flat=True))

    users_movie2 = set(UserPreferences.objects.filter(
        Q(liked_movies=movie2) | Q(disliked_movies=movie2)
    ).values_list('user_id', flat=True))

    common_users = users_movie1.intersection(users_movie2)

    if not common_users:
        return 0.0  # Нет общих пользователей - схожесть 0

    # Для общих пользователей считаем совпадение оценок
    match_count = 0
    for user_id in common_users:
        prefs = UserPreferences.objects.get(user_id=user_id)
        rating1 = 1 if prefs.liked_movies.filter(id=movie1.id).exists() else -1
        rating2 = 1 if prefs.liked_movies.filter(id=movie2.id).exists() else -1

        if rating1 == rating2:
            match_count += 1

    similarity = match_count / len(common_users)
    return similarity


def get_similar_movies(movie, user, limit=5):
    """
    Контекстные рекомендации для страницы фильма
    Гибридный подход: item-based + жанровое пересечение
    """
    # Исключаем уже оцененные пользователем фильмы
    rated_movie_ids = []
    if user.is_authenticated:
        try:
            prefs = UserPreferences.objects.get(user=user)
            rated_movie_ids = list(prefs.liked_movies.values_list('id', flat=True)) + \
                              list(prefs.disliked_movies.values_list('id', flat=True))
        except UserPreferences.DoesNotExist:
            pass

    # 1. Item-based подход - анализируем все фильмы
    item_based_recs = []
    all_movies = Movie.objects.exclude(id=movie.id)

    movie_similarities = []
    for similar_movie in all_movies:
        # Пропускаем уже оцененные пользователем фильмы
        if similar_movie.id in rated_movie_ids:
            continue

        similarity = calculate_item_similarity(movie, similar_movie)
        if similarity > 0.5:  # Порог схожести
            movie_similarities.append((similar_movie, similarity))

    # Сортируем по схожести
    movie_similarities.sort(key=lambda x: x[1], reverse=True)
    item_based_recs = [m for m, s in movie_similarities]

    # 2. Content-based по жанрам (если item-based рекомендаций мало)
    if len(item_based_recs) < limit:
        content_based_recs = Movie.objects.filter(genres__in=movie.genres.all()) \
            .exclude(id=movie.id) \
            .exclude(id__in=rated_movie_ids) \
            .annotate(
            common_genres=Count('genres', filter=Q(genres__in=movie.genres.all())),
            like_count=Count('liked_by')
        ) \
            .order_by('-common_genres', '-year', '-like_count')
        recommendations = list(item_based_recs) + list(content_based_recs)
    else:
        recommendations = item_based_recs

    # Убираем дубликаты
    seen_ids = set()
    unique_recommendations = []
    for rec_movie in recommendations:
        if rec_movie.id not in seen_ids:
            unique_recommendations.append(rec_movie)
            seen_ids.add(rec_movie.id)

    return unique_recommendations[:limit]


def get_new_movies(limit=5):
    """Новые фильмы"""
    return Movie.objects.annotate(
        like_count=Count('liked_by')
    ).order_by('-year', '-like_count')[:limit]


def get_trending_movies(limit=8):
    """Трендовые фильмы"""
    return Movie.objects.annotate(
        like_count=Count('liked_by')
    ).filter(year__gte=2020).order_by('-like_count', '-year')[:limit]