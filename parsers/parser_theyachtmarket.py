#%%
import bs4 as bs
import requests
import pandas as pd
import math
import datetime
import random

MAX_LENGTH = "10"
PRICE_MAX = ""
YEAR_MIN = ""

proxy = {
    'http': 'http://23.227.38.8.9:80'
}

AGENT_LIST = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/78.0.3904.70 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
]

headers = {'User-Agent': random.choice(AGENT_LIST),
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Language': 'en-US,en;q=0.9',
'Accept-Encoding': 'gzip, deflate, br'}

#Scraping all the pages from theyachtmarket.com

url = f"https://www.theyachtmarket.com/en/boats-for-sale/search/?neworused=used&currency=eur&"+ \
f"lengthunit=metres&boattypeids=272&showsail=1&"+ \
f"&priceto={PRICE_MAX}&lengthto={MAX_LENGTH}&yearfrom={YEAR_MIN}"

#Find last page

r = requests.get(url, headers=headers, proxies=proxy)
print(r.status_code)
# IP blocked 🤨
soup = bs.BeautifulSoup(r.text, "lxml")
results_count = soup.find("small")
last_page = int(results_count.text.split()[0].replace("(","").replace(",",""))
print(last_page)
#%%
final_list = []
for page in range(1,last_page+1):
  
    url = f"https://www.theyachtmarket.com/en/boats-for-sale/search/?neworused=used&currency=eur&"+ \
    f"lengthunit=metres&boattypeids=272&showsail=1&"+ \
    f"&priceto={PRICE_MAX}&lengthto={MAX_LENGTH}&yearfrom={YEAR_MIN}&page={str(page)}"

    for ad in soup.findAll("div", {"class" : "col-md-4 col-xs-6 col-xxs-12 text-center listing margin_top_20 listingOrder"}):

        title = ad.find("a" , {"class" : "boat-name"}).text
        link = ad.find("a" , {"class" : "boat-name"}).get("href")
        location = ad.find("strong")
        price = ad.find("span" , {"class" : "pricestyle"}).find("span").text
        specs = ad.find("div" , {"class" : "overview"}).find("span").text.split("|")
        if len(specs) == 4:
            year_built = specs[0]

        details = {"Title" : title, "URL" : link, "Price" : price,"Year Built" : specs,
        "Location" : location}
        final_list.append(details)
df = pd.DataFrame(final_list)
print(df.head())
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

