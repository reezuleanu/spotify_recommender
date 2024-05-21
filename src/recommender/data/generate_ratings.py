"""Genereaza un tabel pentru antrenarea AI ului"""

import pandas as pd

# incarca preferintele
df = pd.read_csv("data/preferinte.csv", delimiter="\t")
df.reset_index(inplace=True)

# reorganizeaza coloanele in formatul [userid, songid, rating]
df_melted = df.melt(id_vars=["index"], var_name="songid", value_name="rating")
df_melted.rename(columns={"index": "userid"}, inplace=True)
df_melted.sort_values(by=["userid", "songid"], inplace=True)

# scrie fisierul csv
df_melted.to_csv("ratings.csv", sep="\t", index=False)
