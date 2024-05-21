import torch
import torch.nn as nn


class RecommenderModel(nn.Module):
    """Model recomandare muzica"""

    def __init__(self, num_users, num_items, num_genres, embedding_size) -> None:
        super().__init__()

        # embedding id utilizator
        self.user_embedding = nn.Embedding(
            num_embeddings=num_users, embedding_dim=embedding_size
        )
        # embedding id melodie
        self.item_embedding = nn.Embedding(
            num_embeddings=num_items, embedding_dim=embedding_size
        )

        # embedding id gen muzical
        self.genre_embedding = nn.Embedding(
            num_embeddings=num_genres, embedding_dim=embedding_size
        )

        # straturi "fully connected" pentru durata si ratie continut explicit
        self.fc_duration = nn.Linear(1, embedding_size)
        self.fc_explicit = nn.Linear(1, embedding_size)

    def forward(
        self,
        user,
        item,
        user_fav_genre,
        item_genre,
        user_avg_duration,
        item_duration,
        user_explicit_ratio,
        item_explicit,
    ):
        """Functie predictie

        Args:
            user (int): id utilizator
            item (int): id melodie
            user_fav_genre (int): id gen favorit utilizator
            item_genre (int): id gen melodie
            user_avg_duration (int): durata medie melodii utilizator
            item_duration (int): durata melodie
            user_explicit_ratio (float): ratie continut explicit utilizator
            item_explicit (bool): continut explicit melodie

        Returns:
            float: sansa sa ii placa utilizatorului melodia
        """
        # introducere id uri utilizator si melodie
        user_emb = self.user_embedding(user)
        item_emb = self.item_embedding(item)

        # introducere id gen utilizator si melodie
        user_genre = self.genre_embedding(user_fav_genre)
        item_genre = self.genre_embedding(item_genre)

        # introducere durata utilizator si melodie
        # normalizare durata
        user_duration = torch.relu(self.fc_duration(user_avg_duration.unsqueeze(-1)))
        item_duration = torch.relu(self.fc_duration(item_duration.unsqueeze(-1)))

        # introducere ratie continut explicit utilizator si daca melodia are continut explicit
        # normalizare continut explicit
        user_explicit = torch.relu(self.fc_explicit(user_explicit_ratio.unsqueeze(-1)))
        item_explicit = torch.relu(self.fc_explicit(item_explicit.unsqueeze(-1)))

        # concatenare matrice pentru utilizator si pentru melodie
        user_data = torch.cat([user_emb, user_genre, user_duration, user_explicit])
        item_data = torch.cat([item_emb, item_genre, item_duration, item_explicit])

        # inmultire matrici si calculat media
        prediction = (user_data * item_data).sum(0).mean()

        # returnare sansa sa ii placa melodia
        return torch.sigmoid(prediction)
