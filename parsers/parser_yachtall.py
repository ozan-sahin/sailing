

import bs4 as bs
import requests
import pandas as pd
#from matplotlib import style
import datetime
#style.use('ggplot')

def parse(YEAR_MIN : str = "2010", PRICE_MAX : str = ""):

    urls = []
    page = ""

    #Find the last page's number
    url = f"https://www.yachtall.com/en/boats/used-boats?ybf={YEAR_MIN}&pg={page}" +\
    f"&sprct={PRICE_MAX}&prc_unit=eur&bcid=23"

    r = requests.get(url)
    soup = bs.BeautifulSoup(r.text, "lxml")
    lis = soup.findAll("span", {"class" : "paging-link"})
    last_page = int(lis[-2].text)


    for page in range(1, last_page+1):
        url = f"https://www.yachtall.com/en/boats/used-boats?ybf={YEAR_MIN}&pg={page}" +\
        f"&sprct={PRICE_MAX}&prc_unit=eur&bcid=23"
        urls.append(url)

    #Scraping all the pages from yachtall.com
    final_list = []

    for url in urls:
        r = requests.get(url)
        soup = bs.BeautifulSoup(r.text, "lxml")
        divs = soup.findAll("div", {"class" : "boatlist-content"})
        for div in divs:
            link = "https://www.yachtall.com" + div.find("h3", {"class" : "boatlist-is-large"}).a.get("href")
            title = div.find("h3", {"class" : "boatlist-is-large"}).text
            price = div.find("span", {"class" : "color-orange-bold nowrap"}).text
            for span in div.findAll("span", ["boatlist-is-large"]):
                if "Sailboat / sailing yacht:" in span.text:
                    info = span.text.strip().split(":")[-1]
                if "Length x beam:" in span.text:
                    dimensions = span.text.strip().split(":")[-1]
                if "built:" in span.text:
                    year_built = span.text.strip().split(",")[0].split(":")[-1]
                if "Engine:" in span.text:
                    engine = span.text.strip().split(":")[-1]
            location = [d.split(":")[-1].strip() for d in div.text.split("\n")  if "Location" in d][0]
            details = {"Title" : title, "URL" : link, "Price" : price, "Engine" : engine,
                    "Info" : info, "Dimensions": dimensions, "Year Built" : year_built,
                    "Location" : location}
            final_list.append(details)
            

    df = pd.DataFrame(final_list)
    df = clean(df)
    return df

def clean(df):
    #Cleaning DataFrame
    import datetime
    df2 = df.drop_duplicates().copy()
    df2["Price"] = df2["Price"].apply(lambda x: x.replace("kr", "").replace("€", "").
                                    replace("$", "").replace("£", "").replace(",","").
                                    replace("A","").replace("C","").strip() ).astype(float)
    df2["Model"] = df2["Info"].apply(lambda x: x.split(",")[0].strip())
    df2["Length"] = df2["Dimensions"].apply(lambda x: float(x.split("x")[0].replace("m", "").strip()))
    df2["Beam"] = df2["Dimensions"].apply(lambda x: float(x.split("x")[-1].replace("m", "").replace(",","").strip()))
    df2["Year Built"] = df2["Year Built"].apply(lambda x: x.replace(" before ", "")).astype("float")
    df2["Age"] = datetime.datetime.now().year - df2["Year Built"]
    df2["Source"] = "yachtall"
    df2["Query_Date"] = datetime.date.today()
    #df2.to_csv("boat_prices_yachtall.csv", sep=";",index=False, encoding="utf-8-sig")

    return df2


