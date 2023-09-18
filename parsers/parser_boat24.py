#%%
import bs4 as bs
import requests
import pandas as pd
import numpy as np
import seaborn as sns
#from matplotlib import style
from matplotlib import pyplot as plt
import datetime

def parse(YEAR_MIN : str = "2010", PRICE_MAX : str = ""):

    #style.use('ggplot')

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'}

    urls = []

    #Find the last page's number
    url = f"https://www.boat24.com/en/sailingboats/sailing-yacht/?jhr_min={YEAR_MIN}" +\
    f"&page=0&sort=datdesc&typ=230&occ=221&whr=EUR&prs_max={PRICE_MAX}"
    r = requests.get(url, headers=headers)
    soup = bs.BeautifulSoup(r.text, "lxml")
    lis = soup.findAll("li", {"class" : "pagination__page"})
    last_page = int(lis[-1].text)


    for page in [str(i*20) for i in range(last_page)]:
        url = f"https://www.boat24.com/en/sailingboats/sailing-yacht/?jhr_min={YEAR_MIN}" +\
        f"&page={page}&sort=datdesc&typ=230&occ=221&whr=EUR&prs_max={PRICE_MAX}"
        urls.append(url)

    #Scraping all the pages from boat24.com
    final_list = []

    for url in urls:
        r = requests.get(url, headers=headers)
        soup = bs.BeautifulSoup(r.text, "lxml")
        divs = soup.findAll("div", {"class" : "blurb"})
        for div in divs:
            details = {key.text : detail.text for  detail,key in zip(div.findAll("span", {"class" : "blurb__value"}),  div.findAll("span", {"class" : "blurb__key"}))}
            details.update({"Title": div.find("h3", {"class" : "blurb__title"}).text,
                            "URL" : div.find("h3", {"class" : "blurb__title"}).a.get("href"),
                            "Location": div.find("p", {"class" : "blurb__location"}).text,
                            "Price" : div.find("aside", {"class" : "blurb__side"}).find("p").text
                            })
            final_list.append(details)

    df = pd.DataFrame(final_list)
    df = clean(df)
    return df

def clean(df):

    #Cleaning DataFrame
    df["Price"] = df["Price"].apply(lambda x: x.replace("EUR", "").replace(",-", "").replace(".", "").strip() )
    df = df.replace("Price on Request", np.nan)
    df = df.replace("Under Offer", np.nan)
    df = df.replace("wanted ad", np.nan)
    df["Price"] = df["Price"].astype(float)
    df["Model"] = df["Title"].apply(lambda x: x.split()[0])
    df["Year Built"] = df["Year Built"].astype("float")
    df["Age"] = datetime.datetime.now().year - df["Year Built"].astype("float")
    #Separate length and beam
    lengths = []
    beams = []
    for pair in df["Dimensions"].str.split(" x ").tolist():
        try:
            if len(pair) == 2:
                l = float(pair[0].replace("m", "").strip())
                b = float(pair[1].replace("m", "").strip())
                if b > l:
                    l , b = b, l
            else:
                l = pair[0].replace("m", "").strip()
                b = np.nan
            lengths.append(l)
            beams.append(b)
        except TypeError:
            lengths.append(np.nan)
            beams.append(np.nan)

    df["Length"] = lengths
    df["Length"] = df["Length"].astype("float")
    df["Beam"] = beams
    df["Beam"] = df["Beam"].astype("float")
    df["Source"] = "boat24"
    df["Query_Date"] = datetime.date.today()
    df = df.rename(columns={'Engine Performance': 'Engine'})
    return df
#%%
#df.to_csv("boat_prices_boat24.csv", sep=";",index=False, encoding="utf-8-sig")
# %%

def analyse(df):
    #Visualisation
    dfBav = df[df["Title"].str.contains("Bénéteau")]
    dfBav.groupby("Year Built").mean("Price")["Price"].plot()
    #%%
    df.query("Length < 15 & Length > 8").groupby("Year Built").mean("Price")["Price"].plot()
    #%%
    df.groupby("Year Built").mean("Price").pct_change()
    #%%
    df.value_counts("Year Built").sort_index().plot(kind="bar")
    #%%
    df["Model"].value_counts(ascending=False)[:10].plot(kind="bar", title="Top 10 Sailboat Sold on Boat24")
    # %%
    df["PricePerLength"] = df["Price"] / df["Length"]
    df.groupby("Year Built").mean("PricePerLength")["PricePerLength"].sort_index().plot(kind="bar", title="Average price per meter €/m")
    #%%

    from sklearn.linear_model import LinearRegression
    df2 = df.dropna().copy()

    # removing ourliers - all the datapoints having z-value larger than 2 are removed
    from scipy import stats
    df2["z_score"] = np.abs(stats.zscore(df2['PricePerLength']))
    df2 = df2[df2["z_score"] < 2]

    x = df2['Age'].values.reshape(-1, 1)
    y = df2['PricePerLength'].replace(0).values
    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]
    intercept = model.intercept_
    equation = f"y = {slope:.2f}x + {intercept:.2f}"
    print(equation)
    down_range = int(df2['Age'].min())
    up_range = int(df2['Age'].max())
    x = [i for i in range(down_range,up_range)]
    predicted_y = model.predict([[i] for i in range(down_range,up_range)]).tolist()
    pd.DataFrame([{i:j for i,j in zip(x,predicted_y)}]).T.plot(title="Price per Length versus Age of the boat")
    # %%
    pd.DataFrame([{i:j for i,j in zip(x,predicted_y)}]).T.pct_change()*100
    #%%
    common_models = df["Model"].value_counts(ascending=False)[:5].index.tolist()
    df_common = df[df["Model"].isin(common_models)]
    df_common.groupby(['Year Built', 'Model'])['Model'].count().unstack().plot(kind="bar", stacked=True)
    # %%
    sns.relplot(x="Year Built", y="Price", hue = "Model", size="PricePerLength",
                sizes=(40, 400), alpha=.5, palette="muted",
                height=10, data=df_common.sort_values(by="Year Built"))
    plt.show()
    #%%
    return