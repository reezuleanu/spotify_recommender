"""Creaza tabel cu utilizatorii si preferintele pentru fiecare item"""

import pandas as pd
import random
from utils import serialize_user_preferences

# incarca datele despre melodii
df = pd.read_csv("muzica.csv", delimiter="\t")

# lista genuri
genres = df["genre"].unique()


# pentru fiecare gen
for genre in genres:
    # pentru 1000 de utilizator per gen
    for i in range(1000):
        # definire gusturi utilizator
        user = []
        # puritatea = sanse sa nu ii placa melodii din alte genuri
        puritate = random.randint(1, 100)
        gusturi = {}
        for j in genres:
            gusturi[j] = random.choice(
                [10, 20, 40, 60, 80]
            )  # sanse sa ii placa alte genuri

        # genul de baza care ii place complet
        gusturi[genre] = 100
        # print(gusturi)

        # definire rating uri
        for _, song in df.iterrows():
            # calcul bazat pe gen si "puritate"
            sansa = gusturi[song["genre"]] / puritate

            # calcul vazat pe popularitatea melodiei si sansa anterioara
            # daca melodia este una din cele 4 genuri, ii imparte popularitatea la 5
            if song["genre"] in ["rock", "clasica", "jazz", "trap"]:
                sansa = song["popularity"] / 5 + sansa
            # altfel, ii adauga 5 la sansa
            else:
                sansa = song["popularity"] + sansa + 5

            if sansa >= 50:
                user.append(1)
                # print(song["genre"], sansa)
            else:
                user.append(-1)
                # print(song["genre"], sansa)

        serialize_user_preferences("preferinte.csv", user)

print("Am terminat de generat preferintele")
