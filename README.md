# Sailing Project
![](https://images.pexels.com/photos/4934616/pexels-photo-4934616.jpeg?auto=compress&cs=tinysrgb&w=640&h=427&dpr=1)

Analysis Repo for Sailing. This repository has been created to perform anaylsis on different sailboats on the market.
    
## To-Do List:
1. Write parsers to collect prices from sailboat websites
2. Collect prices regulary
3. Save the prices into a cloud database
4. Build a multivariate regression model to estimate price of a boat for a given age, size and brand.
5. Compare model estimation to real prices and inform users in case of any cheap boats
6. (Extra) Create a parser for marina costs

## Usage
```python

#PART 1-------------
import pandas as pd
import matplotlib.pyplot as plt

import parser_boat24 as boat24
import parser_yachtall as yachtall
import parser_bandofboats as bandofboats
import parser_yachtworld as yachtworld

YEAR_MIN = "2010"
PRICE_MAX = ""
MAX_LENGTH = "25"
parsers = [yachtworld, bandofboats, yachtall, boat24]
df_list = []

for parser in parsers:
    df = parser.parse(YEAR_MIN=YEAR_MIN, PRICE_MAX=PRICE_MAX, MAX_LENGTH=MAX_LENGTH)
    df_list.append(df)

dataset = pd.concat(df_list)
dataset

#PART 1-------------
