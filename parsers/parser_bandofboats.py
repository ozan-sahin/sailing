import bs4 as bs
import requests
import pandas as pd
import datetime

def parse(YEAR_MIN : str = "2010", PRICE_MAX : str = "", MAX_LENGTH : str = "25"):

    urls = []
    page = "1"

    url =   f"https://www.bandofboats.com/en/boats-for-sale?ref%5B%5D=c%3A9&ref%5B%5D=t%3A37&ref%5B%5D=t%3A39&"+ \
            f"ref%5B%5D=t%3A40&ref%5B%5D=t%3A41&ref%5B%5D=t%3A42&ref%5B%5D=t%3A43&ref%5B%5D=t%3A44&" + \
            f"boat-condition%5B%5D=used&loa_min=&loa_max={MAX_LENGTH}&year_min={YEAR_MIN}&year_max=&price_max={PRICE_MAX}&page={page}"

    #Find the last page's number

    r = requests.get(url)
    soup = bs.BeautifulSoup(r.text, "lxml")
    lis = soup.findAll("li", {"class" : "page-item"})
    last_page = int(lis[-2].text)

    for page in range(1, last_page+1):

        url =   f"https://www.bandofboats.com/en/boats-for-sale?ref%5B%5D=c%3A9&ref%5B%5D=t%3A37&ref%5B%5D=t%3A39&"+ \
                f"ref%5B%5D=t%3A40&ref%5B%5D=t%3A41&ref%5B%5D=t%3A42&ref%5B%5D=t%3A43&ref%5B%5D=t%3A44&" + \
                f"boat-condition%5B%5D=used&loa_min=&loa_max={MAX_LENGTH}&year_min={YEAR_MIN}&year_max=&price_max={PRICE_MAX}&page={page}"

        urls.append(url)

    #Scraping all the pages from bandofboats.com
    final_list = []

    for url in urls:
        r = requests.get(url)
        soup = bs.BeautifulSoup(r.text, "lxml")
        results = soup.findAll("div", {"class" : "search-card-result"})

        for result in results:
            link = "https://www.bandofboats.com" + result.find("a", {"class" : "stretched-link"}).get("href")

            content = result.find("div", {"class" : "search-card-content"})
            title = content.find("h3").text

            spans = content.find("div", {"class" : "d-flex"}).findAll("span")
            
            list1 = [span.text.strip() for span in spans if span.text]
            year_built = list1[0]
            location = list1[2]

            chars = result.find("div", {"class" : "search-card-content-characteristics"}).find("span", {"class" : "mt-2"})
            try:
                list2 = chars.text.strip().split("Beam")
                length = list2[0].split(":")[-1].strip()
                beam = list2[1].split(":")[-1].strip()
            except AttributeError and IndexError:
                length = chars.text.strip().split(":")[-1].strip()
                beam = None

            price = result.find("div", {"class" : "search-card-content-pricing"}).text.strip().split()[0]

            owner = result.find("div", {"class" : "search-card-content-owner"}).text.strip().split("\n")[0]

            details = {"Title" : title, "URL" : link, "Price" : price,
                        "Length" : length, "Beam" : beam,
                        "Year Built" : year_built, "Location" : location}
            final_list.append(details)
                

    df = pd.DataFrame(final_list)
    df = clean(df)
    return df

def clean(df):
    #Cleaning DataFrame

    df2 = df.drop_duplicates().copy()
    df2 = df2[~df2["Price"].str.contains("Price")]
    df2 = df2[~df2["Length"].str.contains("Centreboard")]
    df2["Price"] = df2["Price"].apply(lambda x: x.replace("€", "").replace("," ,"")).astype(float)
    df2["Model"] = df2["Title"].apply(lambda x: x.split(" ")[0].strip())
    df2["Length"] = df2["Length"].apply(lambda x: x.replace("m", "").strip()).astype(float)
    df2["Beam"] = df2["Beam"].apply(lambda x: x.replace("m", "").strip() if not x is None else 0).astype(float)
    df2["Year Built"] = df2["Year Built"].astype("float")
    df2["Age"] = datetime.datetime.now().year - df2["Year Built"]
    df2["Source"] = "bandofboats"
    df2["Query_Date"] = datetime.date.today()
    #df2.to_csv("boat_prices_bandofboats.csv", sep=";",index=False, encoding="utf-8-sig")
    return df2