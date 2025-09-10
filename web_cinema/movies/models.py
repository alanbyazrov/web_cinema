from django.conf import settings
from django.db import models


class Genre(models.Model):
    name = models.CharField(
        max_length=50, unique=True, verbose_name="Название жанра"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название фильма")
    description = models.TextField(blank=True, verbose_name="Описание")
    year = models.IntegerField(verbose_name="Год выпуска")
    director = models.CharField(
        max_length=100, blank=True, verbose_name="Режиссер"
    )
    country = models.CharField(
        max_length=100, blank=True, verbose_name="Страна"
    )
    image_url = models.CharField(
        max_length=300, blank=True, verbose_name="URL изображения"
    )
    genres = models.ManyToManyField(Genre, verbose_name="Жанры")

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"


class UserPreferences(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    favorite_genres = models.ManyToManyField(
        Genre, blank=True, verbose_name="Любимые жанры"
    )
    liked_movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name="liked_by",
        verbose_name="Понравившиеся фильмы",
    )
    disliked_movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name="disliked_by",
        verbose_name="Не понравившиеся фильмы",
    )

    def __str__(self):
        return f"{self.user.phone} preferences"

    class Meta:
        verbose_name = "Предпочтение пользователя"
        verbose_name_plural = "Предпочтения пользователей"


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = [
            "user",
            "movie",
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.phone} - {self.movie.title}"