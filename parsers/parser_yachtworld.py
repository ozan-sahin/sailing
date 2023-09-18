import bs4 as bs
import requests
import pandas as pd
import math
import datetime

def parse(YEAR_MIN : str = "2010", PRICE_MAX : str = "", MAX_LENGTH : str = "25"):
    #Scraping all the pages from yachtworld
    
    #Find last page
    url  =  f"https://www.yachtworld.de/boote-kaufen/zustand-gebraucht/type-segelboote/"+ \
            f"lange-0,{MAX_LENGTH}/preis-0,{PRICE_MAX}/jahr-{YEAR_MIN},2025/"

    r = requests.get(url)
    soup = bs.BeautifulSoup(r.text, "lxml")
    results_count = soup.find("div", {"class" : "results-count"})
    # each page shows 15 results by default
    last_page = math.ceil(float(results_count.text.split()[0].replace(",",""))  / 15 )
    last_page = 250 if last_page > 250 else last_page
    final_list = []
    for page in range(1, last_page+1):

        url  =  f"https://www.yachtworld.de/boote-kaufen/zustand-gebraucht/type-segelboote/klasse-segelyacht/"+ \
                f"lange-0,{MAX_LENGTH}/preis-0,{PRICE_MAX}/jahr-{YEAR_MIN},2025/seite-{str(page)}"

        r = requests.get(url)
        soup = bs.BeautifulSoup(r.text, "lxml")
        results = soup.findAll("li", {"class" : "listing-result"})

        for result in results:
            link = "https://www.yachtworld.de" + result.find("a", {"class" : "inner"}).get("href")

            title = result.find("h2").text
            price = result.find("div", {"class" : "price"}).text
            location = result.find("div", {"class" : "location"}).\
                text.split(result.find("div", {"class" : "location"}).find("div").text)[0]
            length = result.find("div", {"class" : "location"}).find("div").text.split("-")[0].strip()
            year_built = result.find("div", {"class" : "location"}).find("div").text.split("-")[-1].strip()
            owner = result.find("div", {"class" : "offered-by"}).text

            details = {"Title" : title, "URL" : link, "Price" : price,
                        "Length" : length, "Year Built" : year_built, "Location" : location}
            final_list.append(details)

    df = pd.DataFrame(final_list)
    df = clean(df)
    return df

def clean(df):
    #Cleaning DataFrame

    df2 = df.drop_duplicates().copy()
    df2 = df2[~df2["Price"].str.contains("tel. erfragen*")]
    df2["Price"] = df2["Price"].apply(lambda x: x.split("€")[0].replace(".","")).astype(float)
    df2["Model"] = df2["Title"].apply(lambda x: x.split(" ")[1].strip())
    df2["Length"] = df2["Length"].apply(lambda x: x.replace("m", "").strip()).astype(float)
    df2["Year Built"] = df2["Year Built"].astype("float")
    df2["Age"] = datetime.datetime.now().year - df2["Year Built"]
    df2["Source"] = "yachtworld"
    df2["Query_Date"] = datetime.date.today()
    #df2.to_csv("boat_prices_yachtworld.csv", sep=";",index=False, encoding="utf-8-sig")
    return df2

