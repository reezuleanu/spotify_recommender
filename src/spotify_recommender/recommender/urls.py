from django.urls import path
from . import views

urlpatterns = [
    path("", views.hello),
    # path("secret/genres/", views.add_genres),
    # path("secret/tracks/", views.add_tracks),
    path("url/", views.AuthUrl),
    path("callback/", views.spotify_callback),
    path("behavior/", views.generate_behavior),
    path("genres/", views.get_genres),
    path("recommendation/", views.get_recommendation),
    path("rate/", views.rate),
]
