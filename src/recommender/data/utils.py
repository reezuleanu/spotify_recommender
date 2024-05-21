import requests
import sys
import csv
import os
import yaml

from models import TrackData
from exceptions import ExpiredAccessToken


# ! pentru backend
def get_user_code_url(creds: dict) -> str:
    """Genereaza url pentru autentificarea utilizatorului cu Spotify

    Args:
        creds (dict): credidentiale aplicatie si scope

    Returns:
        str: url
    """

    url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={creds['client_id']}&redirect_uri=http://localhost:8000/callback&scope=user-library-read"

    return url


# ! pentru backend
def check_track(access_token: str, *track_ids: str) -> list[bool]:
    """Verifica daca melodiile sunt in Liked Songs pentru un utilizator

    Args:
        access_token (str): token utilizator
        track_ids (str): id uri melodii

    Returns:
        list[bool]: lista rezultat pentru fiecare melodie
    """

    ids = ",".join(track_ids)

    response = requests.get(
        f"https://api.spotify.com/v1/me/tracks/contains?ids={ids}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Nu am putut verifica melodiile, Error {response.status_code}: {response.json()['error']['message']}"
        )


def get_access_token(creds: dict) -> str:
    """Ia token de acces de la Spotify

    Args:
        creds (dict): credidentiale

    Returns:
        str: access token
    """

    response = requests.post("https://accounts.spotify.com/api/token", data=creds)

    if response.status_code == 200:
        # print(response.json())

        access_token = response.json()["access_token"]
        with open("creds.yaml", "r") as fp:
            creds = yaml.safe_load(fp)
        creds["access_token"] = access_token
        with open("creds.yaml", "w") as fp:
            yaml.safe_dump(creds, fp)

        return access_token
    else:
        raise Exception(
            f"Could not get access token, Error {response.status_code}: {response.json()}"
        )


def load_ids(file: str) -> list[str]:
    """Ia id urile dintr-un fisier text

    Args:
        file (str): cale catre fisier

    Returns:
        list[str]: lista id uri din fisier
    """

    with open(file, "r") as fp:
        ids = fp.read()
        return [id for id in ids.split("\n")]


def get_tracks(access_token: str, genre: str, *track_ids: str) -> list[TrackData]:
    """Ia datele despre melodii din baza de date Spotify. Folosit pentru cate un gen
    muzical deodata

    Args:
        access_token (str): token al clientului (nu user)
        genre (str): genul melodiilor
        track_ids (str): lista id uri muzica

    Returns:
        list[TrackData]: lista date melodie
    """
    tracks = []
    for id in track_ids:
        response = requests.get(
            f"https://api.spotify.com/v1/tracks/{id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code == 200:
            data = response.json()
            track_data = TrackData(
                spotifyId=data["id"],
                trackName=data["name"],
                genre=genre,
                artists=[artist["name"] for artist in data["artists"]],
                release_date=data["album"]["release_date"],
                duration=data["duration_ms"],
                popularity=data["popularity"],
                explicit=data["explicit"],
            )
            print(track_data)
            tracks.append(track_data)
        elif response.status_code == 401:
            raise ExpiredAccessToken
        elif response.status_code == 404:
            # incearca sa gaseasca albumul
            response = requests.get(
                f"https://api.spotify.com/v1/albums/{id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            # daca il gaseste
            if response.status_code == 200:
                # itereaza melodiile din raspuns
                popularity = response.json()["popularity"]
                release_date = response.json()["release_date"]
                tracks_in_album = response.json()["tracks"]["items"]
                for data in tracks_in_album:
                    track_data = TrackData(
                        spotifyId=data["id"],
                        trackName=data["name"],
                        genre=genre,
                        artists=[artist["name"] for artist in data["artists"]],
                        release_date=release_date,  # locatia datei e diferita in functie de endpoint
                        duration=data["duration_ms"],
                        popularity=popularity,  # locatia datei e diferita in functie de endpoint
                        explicit=data["explicit"],
                    )
                    print(track_data)
                    tracks.append(track_data)

            # daca nu
            elif response.status_code == 404:
                print(f"Nu am gasit nimic pentru {id}")
            elif response.status_code == 401:
                raise ExpiredAccessToken
            # alte cazuri
            else:
                print(
                    f"Nu am putut lua datele melodiei, Eroare {response.status_code}: {response.json()['error']['message']}"
                )
        else:
            # raise Exception(
            #     f"Nu am putut lua datele melodiei, Error {response.status_code}: {response.json()['error']['message']}"
            # )
            print(
                f"Nu am putut lua datele melodiei, Eroare {response.status_code}: {response.json()['error']['message']}"
            )
    return tracks


def serialize_track_data(file: str, *track_data: TrackData) -> None:
    """Scrie datele melodiei intr-un fisier csv

    Args:
        file (str): nume si locatie fisier
        track_data (TrackData): datele melodiei
    """
    try:
        # coloane
        headers = track_data[0].model_dump()

        # daca fisierul deja exista
        if os.path.isfile(file):
            with open(file, "a") as fp:
                csv_writer = csv.writer(fp, delimiter="\t")
                for track in track_data:
                    csv_writer.writerow(track.model_dump().values())
        # daca fisierul nu exista
        else:
            with open(file, "w") as fp:
                csv_writer = csv.writer(fp, delimiter="\t")
                csv_writer.writerow(headers)
                for track in track_data:
                    csv_writer.writerow(track.model_dump().values())

    except Exception:
        print(f"Nu am putut creea fisierul, eroare: [{sys.exception()}]")


def serialize_user_preferences(file: str, user_preferences: list[int]) -> None:
    try:
        # coloane
        headers = [*range(len(user_preferences))]

        # daca fisierul deja exista
        if os.path.isfile(file):
            with open(file, "a") as fp:
                csv_writer = csv.writer(fp, delimiter="\t")
                csv_writer.writerow(user_preferences)

        # daca fisierul nu exista
        else:
            with open(file, "w") as fp:
                csv_writer = csv.writer(fp, delimiter="\t")
                csv_writer.writerow(headers)
                csv_writer.writerow(user_preferences)

    except Exception:
        print(f"Nu am putut creea fisierul, eroare: [{sys.exception()}]")


def serialize_user_behavior(file: str, user_behavior: list) -> None:
    try:
        # coloane
        headers = ["fav_genre", "average_duration", "average_year", "explicit_ratio"]

        # daca fisierul deja exista
        if os.path.isfile(file):
            with open(file, "a") as fp:
                csv_writer = csv.writer(fp, delimiter="\t")
                csv_writer.writerow(user_behavior)

        # daca fisierul nu exista
        else:
            with open(file, "w") as fp:
                csv_writer = csv.writer(fp, delimiter="\t")
                csv_writer.writerow(headers)
                csv_writer.writerow(user_behavior)

    except Exception:
        print(f"Nu am putut creea fisierul, eroare: [{sys.exception()}]")
