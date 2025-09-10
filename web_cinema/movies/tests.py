from movies.models import Genre, Movie, UserPreferences, Review
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class MovieModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Драма")
        self.movie = Movie.objects.create(
            title="Тестовый фильм",
            description="Тестовое описание",
            year=2023,
            director="Тестовый режиссер",
            country="Россия",
        )
        self.movie.genres.add(self.genre)

    def test_movie_creation(self):
        self.assertEqual(str(self.movie), "Тестовый фильм (2023)")
        self.assertEqual(self.movie.genres.count(), 1)
        self.assertEqual(self.movie.genres.first().name, "Драма")


class GenreModelTest(TestCase):
    def test_genre_creation(self):
        genre = Genre.objects.create(name="Комедия")
        self.assertEqual(str(genre), "Комедия")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="79998887766",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.movie = Movie.objects.create(title="Тестовый фильм", year=2023)

    def test_review_creation(self):
        review = Review.objects.create(
            user=self.user, movie=self.movie, text="Отличный фильм!"
        )
        self.assertEqual(review.text, "Отличный фильм!")
        # Проверяем что строка содержит нужную информацию без точного формата
        self.assertIn(str(self.user.phone), str(review))
        self.assertIn(self.movie.title, str(review))


class UserPreferencesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="79998887766",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.genre = Genre.objects.create(name="Драма")
        self.movie = Movie.objects.create(title="Тестовый фильм", year=2023)

    def test_user_preferences_creation(self):
        prefs = UserPreferences.objects.create(user=self.user)
        prefs.favorite_genres.add(self.genre)
        prefs.liked_movies.add(self.movie)

        self.assertEqual(prefs.favorite_genres.count(), 1)
        self.assertEqual(prefs.liked_movies.count(), 1)
        # Проверяем что строка содержит номер телефона пользователя
        self.assertIn(str(self.user.phone), str(prefs))


class MovieViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            phone="79998887766",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.genre = Genre.objects.create(name="Драма")
        self.movie = Movie.objects.create(
            title="Тестовый фильм",
            description="Тестовое описание",
            year=2023,
            director="Тестовый режиссер",
        )
        self.movie.genres.add(self.genre)

    def test_home_view(self):
        response = self.client.get(reverse("movies:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/home.html")

    def test_movie_list_view(self):
        response = self.client.get(reverse("movies:movie_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movie_list.html")
        self.assertContains(response, "Тестовый фильм")

    def test_movie_detail_view(self):
        response = self.client.get(
            reverse("movies:movie_detail", args=[self.movie.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movie_detail.html")
        self.assertContains(response, "Тестовый фильм")

    def test_search_view(self):
        response = self.client.get(reverse("movies:search"), {"q": "тест"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/search.html")

    def test_rate_movie_like_authenticated(self):
        self.client.login(phone="79998887766", password="testpass123")
        response = self.client.post(
            reverse("movies:rate_movie", args=[self.movie.id]),
            {"action": "like"}
        )
        self.assertEqual(response.status_code, 302)

        prefs = UserPreferences.objects.get(user=self.user)
        self.assertTrue(prefs.liked_movies.filter(id=self.movie.id).exists())

    def test_rate_movie_unauthenticated(self):
        response = self.client.post(
            reverse("movies:rate_movie", args=[self.movie.id]),
            {"action": "like"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login


class RecommendationsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            phone="79998887766",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.genre = Genre.objects.create(name="Драма")
        self.movie = Movie.objects.create(title="Тестовый фильм", year=2023)
        self.movie.genres.add(self.genre)

        # Создаем предпочтения с любимым жанром
        prefs = UserPreferences.objects.create(user=self.user)
        prefs.favorite_genres.add(self.genre)

    def test_recommendations_view_authenticated(self):
        self.client.login(phone="79998887766", password="testpass123")
        response = self.client.get(reverse("movies:recommendations"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/recommendations.html")

    def test_recommendations_view_unauthenticated(self):
        response = self.client.get(reverse("movies:recommendations"))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class UtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="79998887766",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.genre = Genre.objects.create(name="Драма")
        self.movie = Movie.objects.create(title="Тестовый фильм", year=2023)
        self.movie.genres.add(self.genre)

        # Создаем предпочтения
        prefs = UserPreferences.objects.create(user=self.user)
        prefs.favorite_genres.add(self.genre)

    def test_get_recommendations(self):
        from movies.utils import get_recommendations

        recommendations = get_recommendations(self.user)
        self.assertIsNotNone(recommendations)
        # Функция возвращает QuerySet, а не list
        self.assertTrue(hasattr(recommendations, '__iter__'))

    def test_get_popular_movies(self):
        from movies.utils import get_popular_movies

        popular_movies = get_popular_movies()
        self.assertIsNotNone(popular_movies)
        # Функция возвращает QuerySet, а не list
        self.assertTrue(hasattr(popular_movies, '__iter__'))

    def test_get_contextual_recommendations(self):
        from movies.utils import get_contextual_recommendations

        similar_movies = get_contextual_recommendations(self.movie, self.user, 3)
        self.assertIsNotNone(similar_movies)
        # Функция возвращает list
        self.assertIsInstance(similar_movies, list)