#%%
import bs4 as bs
import datetime
import pandas as pd


with open("sahibinden.txt", "r" , encoding="utf8") as file:
    source = file.read()
# %%
df = pd.concat(pd.read_html(source))
df = df.drop(columns=["Unnamed: 0", "Unnamed: 8"], axis=1).reset_index(drop=True).dropna()
df["Query_Date"] = datetime.date.today()
df
# %%
