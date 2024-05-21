from .models import Token, User, Track, Rating, Genre
from django.utils import timezone
from datetime import timedelta
from statistics import mean
import requests


def create_or_update_token(
    user_id, access_token, token_type, expires_in, refresh_token
):
    tokens = Token.objects.filter(userid=user_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    if tokens.exists():
        token = tokens[0]
        token.access_token = access_token
        token.tip_token = token_type
        token.expira_la = expires_in
        token.refresh_token = refresh_token
        token.save(
            update_fields=["access_token", "refresh_token", "expira_la", "tip_token"]
        )

    else:
        token = Token(
            userid=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            tip_token=token_type,
            expira_la=expires_in,
        )
        token.save()


def add_rating(userid, songid, rating_value):
    ratings = Rating.objects.filter(userid=userid, songid=songid)
    if ratings.exists():
        rating = ratings[0]
        rating.rating = rating_value
        rating.save(update_fields=["rating"])
    else:
        rating = Rating(userid=userid, songid=songid, rating=rating_value)
        rating.save()


def add_user_ratings(spotifyid, token) -> None:
    id = User.objects.filter(spotifyid=spotifyid)[0].id

    tracks = Track.objects.all()

    for track in tracks:
        response = requests.get(
            f"https://api.spotify.com/v1/me/tracks/contains?ids={track.spotifyid}",
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        if response[0] is True:
            add_rating(id, track.id, 1)


def get_user_behavior(userid) -> dict:
    ratings = Rating.objects.filter(userid=userid)
    genres = {}
    durations = []
    years = []
    explicit = []
    for rating in ratings:
        if rating.rating == 1:
            track = Track.objects.filter(id=rating.songid)[0]
            genre = Genre.objects.filter(id=track.genreid)[0].genre
            if genre in genres.keys():
                genres[genre] += 1
            else:
                genres[genre] = 1

            durations.append(track.durationms)
            years.append(track.releasedate.year)
            explicit.append(int(track.explicit))

    fav_genre = max(genres, key=genres.get)
    avg_duration = mean(durations)
    avg_year = mean(years)
    explicit = mean(explicit)

    return {
        "fav_genre": fav_genre,
        "avg_duration": avg_duration,
        "avg_year": avg_year,
        "explicit": explicit,
    }


def add_user_behavior(userid, behavior) -> None:
    user = User.objects.filter(id=userid)[0]

    user.favoriteGenreId = Genre.objects.filter(genre=behavior["fav_genre"])[0].id
    user.averageDuration = behavior["avg_duration"]
    user.averageYear = behavior["avg_year"]
    user.explicitRatio = behavior["explicit"]

    user.save(
        update_fields=[
            "favoriteGenreId",
            "averageDuration",
            "averageYear",
            "explicitRatio",
        ]
    )


def create_user(user_id) -> int:
    users = User.objects.filter(spotifyid=user_id)

    if users.exists():
        return users[0].id

    else:
        user = User(spotifyid=user_id)
        user.save()
        return user.id
