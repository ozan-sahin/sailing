#%%

# import bs4 as bs
# import requests
# import numpy as np
# import datetime

#%%
import pandas as pd
import timeit
import matplotlib.pyplot as plt

import parser_boat24 as boat24
import parser_yachtall as yachtall
import parser_bandofboats as bandofboats
import parser_yachtworld as yachtworld
import parser_theyachtmarket as theyachtmarket

YEAR_MIN = "2010"
PRICE_MAX = ""
MAX_LENGTH = "25"

parsers = [theyachtmarket, yachtworld, bandofboats, yachtall, boat24]

# %%
df_list = []
for parser in parsers:
    start = timeit.default_timer()
    df = parser.parse(YEAR_MIN=YEAR_MIN, PRICE_MAX=PRICE_MAX)
    stop = timeit.default_timer()
    print('Time ' + parser.__name__ + ": ", int(stop - start))
    df_list.append(df)
# %%
dataset = pd.concat(df_list)
dataset
# %%
dataset["Source"].value_counts().plot(kind ="barh", title="Source Distribution")
plt.show()
dataset["Year Built"].plot(kind="hist", title="Year Distribution")
plt.show()
dataset.query("Price <= 1000000")["Price"].plot(kind="hist", title="Price Distribution")
plt.show()
# %%
