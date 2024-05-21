"""genereaza csv cu datele despre utilizatori"""

import pandas as pd
import datetime
from statistics import mean
from utils import serialize_user_behavior

# genul fiecarei melodii
muzica = pd.read_csv("muzica.csv", delimiter="\t")

# rating ul fiecarei melodii
preferinte = pd.read_csv("preferinte.csv", delimiter="\t")


def calculate_behavior() -> None:
    """Functie care calculeaza un "behavior" pentru fiecare utilizator pe baza preferintelor generate"""

    for userid, user in preferinte.iterrows():
        genre_count = {}
        durations = []
        release_years = []
        explicit_content = []

        for songid, song in muzica.iterrows():
            if user[songid] == 1:
                # genre count
                if song["genre"] in genre_count.keys():
                    genre_count[song["genre"]] += 1
                else:
                    genre_count[song["genre"]] = 1

                # duration
                durations.append(song["duration"])

                # release year
                release_years.append(
                    datetime.datetime.fromisoformat(song["release_date"]).year
                )

                # explicit content ratio
                explicit_content.append(int(song["explicit"]))

            else:
                continue

        print(genre_count)
        # handle data
        favorite_genre = max(genre_count, key=genre_count.get)
        print(favorite_genre)

        s = 0
        for duration in durations:
            s += duration
        average_duration = int(s / len(durations))

        s = 0
        for year in release_years:
            s += year
        average_year = int(s / len(release_years))

        explicit_content_ratio = mean(explicit_content)

        user_data = [
            favorite_genre,
            average_duration,
            average_year,
            explicit_content_ratio,
        ]
        # print(user_data)

        serialize_user_behavior("utilizatori.csv", user_data)


if __name__ == "__main__":
    calculate_behavior()


# user = [userid: int, favorite_genre: str, average_duration_ms: int, average_release_year: int, explicit_content_ratio: float] 5
# item = [itemid: int, genre: str, duration_ms: int, release_year: int, explicit_content: bool] 5
