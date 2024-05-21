import pandas as pd
from torch.utils.data import Dataset
from datetime import datetime


class TrackDataset(Dataset):
    """Dataset pentru antrenat modelul"""

    def __init__(self, df, users, songs) -> None:
        super().__init__()

        self.df = df[["userid", "songid", "rating"]]  # ratings.csv
        self.users = users  # utilizatori.csv
        self.songs = songs[
            ["genre", "duration", "release_date", "explicit"]
        ]  # muzica.csv
        self.genres = [*self.songs["genre"].unique()]  # lista genuri
        self.x_user_song = list(
            zip(self.df.userid.values, self.df.songid.values)
        )  # iterabil utilizator-melodie
        self.y_rating = self.df.rating.values  # rating

    def __len__(self):
        return len(self.y_rating)

    def __getitem__(self, idx):

        # formatare user
        user = [self.x_user_song[idx][0], *self.users.iloc[self.x_user_song[idx][0]]]
        user[1] = self.genres.index(user[1])  # transforma genul intr-un int

        # formatare song
        song = [self.x_user_song[idx][1], *self.songs.iloc[self.x_user_song[idx][1]]]
        song[1] = self.genres.index(song[1])  # transforma genul intr-un int
        song[3] = datetime.fromisoformat(song[3]).year  # ia anul din data lansarii
        song[4] = int(song[4])  # conversie bool -> int

        # formatare rating
        rating = self.y_rating[idx]
        if rating == -1:
            rating = 0

        # returneaza date utilizator si melodie, si rating ul pentru verificare
        return [user, song], rating
