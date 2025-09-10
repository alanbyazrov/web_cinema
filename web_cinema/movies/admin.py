from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Movie, UserPreferences, Review


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["image_preview", "title", "year", "director", "country", "get_like_count", "get_dislike_count"]
    list_display_links = ["image_preview", "title"]
    list_filter = ["year", "genres", "country"]
    search_fields = ["title", "director"]
    filter_horizontal = ["genres"]
    readonly_fields = ["image_preview_large"]

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "description",
                    "year",
                    "director",
                    "country",
                )
            },
        ),
        ("Изображение", {"fields": ("image_url", "image_preview_large")}),
        ("Жанры", {"fields": ("genres",)}),
    )

    def get_like_count(self, obj):
        return obj.liked_by.count()
    get_like_count.short_description = "Лайков"

    def get_dislike_count(self, obj):
        return obj.disliked_by.count()
    get_dislike_count.short_description = "Дизлайков"

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 80px; object-fit: cover;" />',
                obj.image_url
            )
        return "Нет изображения"
    image_preview.short_description = "Превью"

    def image_preview_large(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 100%; object-fit: contain;" /><br><small>{}</small>',
                obj.image_url, obj.image_url
            )
        return "Нет изображения"
    image_preview_large.short_description = "Предпросмотр изображения"

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ["user", "get_favorite_genres", "get_liked_count", "get_disliked_count"]
    filter_horizontal = ["favorite_genres", "liked_movies", "disliked_movies"]

    def get_favorite_genres(self, obj):
        return ", ".join([genre.name for genre in obj.favorite_genres.all()])
    get_favorite_genres.short_description = "Любимые жанры"

    def get_liked_count(self, obj):
        return obj.liked_movies.count()
    get_liked_count.short_description = "Лайков"

    def get_disliked_count(self, obj):
        return obj.disliked_movies.count()
    get_disliked_count.short_description = "Дизлайков"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "created_at", "short_text")
    list_filter = ("created_at", "movie")
    search_fields = ("user__phone", "movie__title", "text")
    readonly_fields = ("created_at",)

    def short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    short_text.short_description = "Текст отзыва"