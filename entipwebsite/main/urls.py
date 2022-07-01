# represent the urls that go to different views in views.py
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views    # import views from current directory

urlpatterns = [
    path("", views.home, name="home"),
    path("movies/", views.movies, name="movies"),
    path("series/", views.series, name="series"),
    path("songs/", views.songs, name="songs"),
]
urlpatterns += staticfiles_urlpatterns()
