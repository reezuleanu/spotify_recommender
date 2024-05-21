"""Programul asta se ocupa cu achizitia datelor despre melodii de la Spotify"""

import os
import threading
from utils import (
    get_access_token,
    get_tracks,
    load_ids,
    serialize_track_data,
)
from exceptions import ExpiredAccessToken
import yaml

# incarca credidentiale din yaml
with open("creds.yaml", "r") as fp:
    creds = yaml.safe_load(fp)

    clientID = creds["clientID"]
    clientSecret = creds["clientSecret"]
    access_token = creds["access_token"]


creds = {
    # "code": "AQDahNmA8nie8g2LinISYsd7waazTnS0vSmIeIU5l4ZMDmKp7NNUNkTV2WdxtTejBbCcLbS5WXZH8HIzQ_pT2dWoA94a4RW5u5jJIXzvFN3Skos5je83hSHF2qzb_Mo4HAt-LLrVWV82Sc1a0lid2nxgEcKEgIzAFE0CxQqAnVROOfGqjeLEsh0OP6JR8qCfISadwL0",
    # "redirect_uri": "http://localhost:8000/callback",
    # "grant_type": "authorization_code",
    "grant_type": "client_credentials",
    "client_id": clientID,
    "client_secret": clientSecret,
}


def get_data(ACCESS_TOKEN: str, filename: str) -> None:
    """Ia datele pentru un fisier text (fiecare reprezinta cate un gen muzical)

    Args:
        ACCESS_TOKEN (str): token de acces client
        filename (str): fisier text continand id uri pentru un gen muzical
    """

    # incarca id urile dintr-un fisier text
    ids = load_ids(f"{filename}")

    # ia numele genului din numele fisierului
    genre = filename.rstrip(".txt")

    # ia datele melodiilor
    try:
        tracks = get_tracks(ACCESS_TOKEN, genre, *ids)

    # daca token ul a expirat, ia altul, il scrie in yaml, si incearca
    # sa ia iar informatiile despre melodii
    except ExpiredAccessToken:
        ACCESS_TOKEN = get_access_token(creds)
        with open("creds.yaml", "w") as fp:
            yaml.safe_dump(
                {
                    "clientID": creds["client_id"],
                    "clientSecret": creds["client_secret"],
                    "access_token": ACCESS_TOKEN,
                },
                fp,
            )
        tracks = get_tracks(ACCESS_TOKEN, genre, *ids)
    finally:
        # scrie datele despre melodii intr-un fisier csv
        serialize_track_data("muzica.csv", *tracks)


# magie cu multithreading
if __name__ == "__main__":

    # lista cu fisierele text
    filenames = [filename for filename in os.listdir() if filename.endswith(".txt")]

    # creeaza cate un thread pentru fiecare gen muzical
    workers = []
    for i in range(len(filenames)):
        workers.append(
            threading.Thread(
                target=get_data,
                args=(
                    access_token,
                    filenames[i],
                ),
            )
        )

    # porneste thread urile
    for worker in workers:
        worker.start()

    # inchide thread urile dupa ce si-au terminat treaba
    for worker in workers:
        worker.join()

    # ! Chestia asta e prea rapida si ma refuza API ul
    # single threaded
    for filename in filenames:
        get_data(access_token, filename)
