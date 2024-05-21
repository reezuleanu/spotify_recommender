from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from .models import Genre, Track, User, Token, Rating
from .utils import (
    create_or_update_token,
    create_user,
    add_user_behavior,
    get_user_behavior,
    add_user_ratings,
    add_rating,
)
import requests
import yaml
from datetime import datetime
from .model import RecommenderModel
import torch
from random import randint

# foloseste placa video daca disponibila
if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"


mdl = RecommenderModel(10000, 974, 10, 32)
mdl.load_state_dict(torch.load("recommender/model.pth"))


with open("recommender/creds.yaml", "r") as fp:
    creds = yaml.safe_load(fp)

REDIRECT_URI = creds["redirectURI"]
CLIENT_ID = creds["clientID"]
CLIENT_SECRET = creds["clientSecret"]


# Create your views here.


@api_view(["GET"])
def hello(request) -> Response:
    return Response("salut")


# ! One time use
@api_view(["GET"])
def add_tracks(request) -> Response:
    df = pd.read_csv("../recommender/data/muzica.csv", delimiter="\t")
    for _, row in df.iterrows():
        track = Track(
            spotifyid=row["spotifyId"],
            genreid=Genre.objects.filter(genre=row["genre"])[0].id,
            artists="".join(row["artists"]),
            releasedate=datetime.fromisoformat(row["release_date"]),
            durationms=row["duration"],
            popularity=row["popularity"],
            explicit=row["explicit"],
        )
        if Track.objects.filter(spotifyid=track.spotifyid).exists():
            continue
        track.save()
    return Response("Tracks added successfully")


# ! One time use
@api_view(["GET"])
def add_genres(request) -> Response:
    """Endpoint de adaugat genurile in baza de date"""

    df = pd.read_csv("../recommender/data/muzica.csv", delimiter="\t")
    genres = df["genre"].unique()
    added_genres = Genre.objects.all()
    for genre in genres:
        data = Genre(genre=genre)
        if data in added_genres:
            continue
        data.save()

    return Response("totul a mers ok")


@api_view(["GET"])
def AuthUrl(request) -> Response:
    """Generare URL de autentificare cu Spotify"""

    scopes = "user-read-private user-read-email user-library-read"

    url = f"https://accounts.spotify.com/authorize?scope={scopes}&response_type=code&redirect_uri={REDIRECT_URI}&client_id={CLIENT_ID}"

    return Response({"url": url})


@api_view(["GET"])
def spotify_callback(request) -> Response:
    code = request.GET.get("code")
    error = request.GET.get("error")

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    ).json()

    if "error" in response.keys():
        error = response["error"]
        return Response({"error": error})

    access_token = response["access_token"]
    token_type = response["token_type"]
    refresh_token = response["refresh_token"]
    expires_in = response["expires_in"]

    user_profile = requests.get(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"{token_type} {access_token}"},
    ).json()

    user_id = user_profile["id"]
    create_user(user_id)
    create_or_update_token(user_id, access_token, token_type, expires_in, refresh_token)

    return redirect(f"http://localhost:3000/?token={access_token}")


@api_view(["GET"])
def generate_behavior(request) -> Response:
    token = request.GET.get("token")

    spotifyid = Token.objects.filter(access_token=token)[0].userid
    userid = User.objects.filter(spotifyid=spotifyid)[0].id
    add_user_ratings(spotifyid, token)
    add_user_behavior(userid, get_user_behavior(userid))

    return Response("Behavior added successfully")


@api_view(["GET"])
def get_genres(request) -> Response:
    genres = [genre.genre for genre in Genre.objects.all()]

    return Response({"genres": genres})


@api_view(["GET"])
def get_recommendation(request) -> Response:
    token = request.GET.get("token")
    gen = request.GET.get("gen")
    manele = request.GET.get("manele")

    user_spotifyid = Token.objects.filter(access_token=token)[0].userid
    user = User.objects.filter(spotifyid=user_spotifyid)[0]

    if gen != "any":
        genres = Genre.objects.filter(genre=gen)
    elif manele == "false":
        genres = Genre.objects.exclude(genre="manele")
    else:
        genres = Genre.objects.all()

    already_rated = Rating.objects.filter(userid=user.id)
    already_rated = [rating.rating for rating in already_rated]

    tracks = Track.objects.filter(genreid__in=[genre.id for genre in genres]).exclude(
        id__in=already_rated
    )
    # date despre utilizator pentru model
    user_data = [
        user.id - 1,
        user.favoriteGenreId - 1,
        user.averageDuration,
        user.explicitRatio,
    ]
    song_ratings = {}

    for track in tracks:
        # date despre melodie pentru model
        song_data = [track.id - 1, track.genreid - 1, track.durationms, track.explicit]

        # initializare tensori:
        xUser = torch.tensor(user_data[0], dtype=torch.long)
        xItem = torch.tensor(song_data[0], dtype=torch.long)

        xUserGenre = torch.tensor(user_data[1], dtype=torch.long)
        xItemGenre = torch.tensor(song_data[1], dtype=torch.long)

        xUserDuration = torch.tensor(user_data[2], dtype=torch.float32)
        xItemDuration = torch.tensor(song_data[2], dtype=torch.float32)

        xUserExplicit = torch.tensor(user_data[3], dtype=torch.float32)
        xItemExplicit = torch.tensor(song_data[3], dtype=torch.float32)

        prediction = mdl(
            xUser,
            xItem,
            xUserGenre,
            xItemGenre,
            xUserDuration,
            xItemDuration,
            xUserExplicit,
            xItemExplicit,
        )

        song_ratings[track.spotifyid] = float(prediction)

    # sortare rating uri de la cel mai mare in jos
    recommendations = dict(
        sorted(song_ratings.items(), key=lambda x: x[1], reverse=True)
    )

    # luam id urile in ordine
    ids = list(recommendations.keys())

    # returnam un id random din cele top 10
    return Response({"song": ids[randint(0, 10)]})


@api_view(["GET"])
def rate(request) -> Response:
    user_token = request.GET.get("user")
    song_spotify = request.GET.get("song")
    rating = request.GET.get("rating")

    user_spotify = Token.objects.filter(access_token=user_token)[0].userid

    userid = User.objects.filter(spotifyid=user_spotify)[0].id
    songid = Track.objects.filter(spotifyid=song_spotify)[0].id

    if rating == "like":
        rating = 1
    elif rating == "dislike":
        rating = 0
    else:
        return Response("Invalid rating", 401)

    add_rating(userid, songid, rating)

    return Response("Rating added successfully")
