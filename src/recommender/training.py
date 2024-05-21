"""Script antrenare model"""

import pandas as pd
import torch
from torch import optim
import torch.nn as nn
from torch.utils.data import DataLoader
from dataset import TrackDataset
from model import RecommenderModel
import numpy as np

# foloseste placa video daca disponibila
if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

# incarcare date antrenare
df = pd.read_csv("data/ratings.csv", delimiter="\t")
_val = int(len(df) / 3)  # cate date vor fi pentru validare (33%)

# date pentru antrenare
df_train = df.head(-_val).reset_index(drop=True)

# date pentru validare
df_val = df.tail(_val).reset_index(drop=True)

# date despre utilizatori si melodii
users = pd.read_csv("data/utilizatori.csv", delimiter="\t")
songs = pd.read_csv("data/muzica.csv", delimiter="\t")

# initializare datasets
ds_train = TrackDataset(df_train, users, songs)
ds_val = TrackDataset(df_val, users, songs)


def training(mdl) -> None:
    """Functie pentru procesul de antrenare"""

    # marime batch size (cate date vor fi date modelului deodata)
    BS = 1
    # dataloader pentru antrenare
    dl_train = DataLoader(ds_train, BS, shuffle=True)
    # dataloader pentru validare
    dl_val = DataLoader(ds_val, BS, shuffle=True)

    # learning rate
    LR = 0.2
    # numar epoci
    NUM_EPOCHS = 100

    # optimizator automat
    opt = optim.AdamW(mdl.parameters(), lr=LR)
    # functie de calcul a erorii
    loss_fn = nn.MSELoss()

    # buffer erori per epoca (pentru calcul eroare medie)
    epoch_train_losses, epoch_val_losses = [], []

    print(f"Folosesc {device}")
    print(f"Date antrenare: {len(df_train)}")
    print(f"Date validare: {len(df_val)}")

    for epoch in range(NUM_EPOCHS):
        # calcul eroare medie per antrenament epoca
        train_losses, val_losses = [], []
        mdl.train()
        i = 0
        y = 1
        for utilizator_melodie, rating in dl_train:

            # se incarca datele din batch in memoria dispozitivului
            xUser = utilizator_melodie[0][0].to(device, dtype=torch.long)
            xItem = utilizator_melodie[1][0].to(device, dtype=torch.long)

            xUserGenre = utilizator_melodie[0][1].to(device, dtype=torch.long)
            xItemGenre = utilizator_melodie[1][1].to(device, dtype=torch.long)

            xUserDuration = utilizator_melodie[0][2].to(device, dtype=torch.float32)
            xItemDuration = utilizator_melodie[1][2].to(device, dtype=torch.float32)

            xUserExplicit = utilizator_melodie[0][3].to(device, dtype=torch.float32)
            xItemExplicit = utilizator_melodie[1][3].to(device, dtype=torch.float32)

            yRatings = rating.to(device, dtype=torch.float32)

            # modelul prezice rating ul
            preds = mdl(
                xUser,
                xItem,
                xUserGenre,
                xItemGenre,
                xUserDuration,
                xItemDuration,
                xUserExplicit,
                xItemExplicit,
            )
            # calculare automata functie eroare
            loss = loss_fn(
                torch.tensor([preds], device=device, requires_grad=True), yRatings
            )
            train_losses.append(loss.item())

            # optimizare automata
            opt.zero_grad()
            loss.backward()
            opt.step()

            i += 1
            if i >= 1000:
                print(f"Antrenat pe {device} tura {i*y}, rezultat: {preds} | {rating}")
                print("Eroare: ", loss)
                print(f"Antrenament: {round(((y*i)/len(df_train))*100,2)}%", end="\r")
                i = 0
                y += 1
        print("Antrenament: 100%")
        mdl.eval()
        i = 0
        y = 1
        for utilizator_melodie, rating in dl_val:

            # se incarca datele din batch in memoria dispozitivului
            xUser = utilizator_melodie[0][0].to(device, dtype=torch.long)
            xItem = utilizator_melodie[1][0].to(device, dtype=torch.long)

            xUserGenre = utilizator_melodie[0][1].to(device, dtype=torch.long)
            xItemGenre = utilizator_melodie[1][1].to(device, dtype=torch.long)

            xUserDuration = utilizator_melodie[0][2].to(device, dtype=torch.float32)
            xItemDuration = utilizator_melodie[1][2].to(device, dtype=torch.float32)

            xUserExplicit = utilizator_melodie[0][3].to(device, dtype=torch.float32)
            xItemExplicit = utilizator_melodie[1][3].to(device, dtype=torch.float32)

            yRatings = rating.to(device, dtype=torch.float32)

            # modelul prezice rating ul
            preds = mdl(
                xUser,
                xItem,
                xUserGenre,
                xItemGenre,
                xUserDuration,
                xItemDuration,
                xUserExplicit,
                xItemExplicit,
            )

            # calculare automata functie eroare
            loss = loss_fn(
                torch.tensor([preds], device=device, requires_grad=True), yRatings
            )
            val_losses.append(loss.item())

            i += 1
            if i > 1000:
                print(f"Validare pe {device} tura {i*y}, Rezultat: {preds} | {rating}")
                print("Eroare: ", loss)
                print(f"Validare: {round(((y*i)/len(df_val))*100, 2)}%", end="\r")
                i = 0
                y += 1
                # if y == 3:
                #     break
        print("Validare: 100%")

        epoch_train_loss = np.mean(train_losses)
        epoch_val_loss = np.mean(val_losses)
        epoch_train_losses.append(epoch_train_loss)
        epoch_val_losses.append(epoch_val_loss)
        print(
            f"Epoca: {epoch}, Eroare antrenare: {epoch_train_loss}, Eroare validare:{epoch_val_loss}"
        )


if __name__ == "__main__":

    try:
        # incarcare model
        mdl = RecommenderModel(10000, 974, 10, 32)
        mdl.load_state_dict(torch.load("model.pth"))
        mdl.to(device)

        # incepere proces antrenare
        training(mdl)

    # daca se inchide programul prematur
    except KeyboardInterrupt:
        print("\nAi inchis procesul de antrenare")

    finally:
        # salvare parametri model
        torch.save(mdl.state_dict(), "model.pth")
        print("\nModel salvat cu succes!")
