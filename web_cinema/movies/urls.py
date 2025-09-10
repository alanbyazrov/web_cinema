from django.urls import path

from . import views


app_name = "movies"

urlpatterns = [
    path("", views.home, name="home"),
    path("movies/", views.movie_list, name="movie_list"),
    path("search/", views.search, name="search"),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("movie/<int:movie_id>/review/", views.add_review, name="add_review"),
    path("movie/<int:movie_id>/rate/", views.rate_movie, name="rate_movie"),
    path(
        "preferences/",
        views.set_genre_preferences,
        name="set_genre_preferences",
    ),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("my-ratings/", views.my_ratings, name="my_ratings"),
]
