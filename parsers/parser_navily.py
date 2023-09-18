#%%
import bs4 as bs
import requests
import pandas as pd
import datetime
import json

#%%
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Language': 'en-US,en;q=0.9',
'Accept-Encoding': 'gzip, deflate, br'}

with open('greek_marinas.txt','r') as file:
    urls = file.read().splitlines()
#%%
#Scraping all the pages from navily.com
df_list = []

for url in urls:
    r = requests.get(url, headers=headers)
    soup = bs.BeautifulSoup(r.text, "lxml")
    try:
        container = soup.find("div", {"class" : "container mt-4 about-section"}).find("port-description-component")[":port"]
        myDict = json.loads(container)
        raw_df = pd.DataFrame([myDict])
        df_list.append(raw_df)
    except AttributeError:
        continue
#%%
dataset = pd.concat(df_list).reset_index(drop=True)
dataset.to_csv("navily_marina_database_greece.csv", sep=";",index=False, encoding="utf-8-sig")
dataset
#%%
def process_htmls(filename : str = "navily - Greece.txt"):
    with open(filename, "r" , encoding="utf8") as file:
        source = file.read()
    soup = bs.BeautifulSoup(source, "lxml")
    list_url = []
    for tag in soup.findAll("a"):
        try:
            if "port" in tag.get("href"):
                list_url.append(tag.get("href"))
        except TypeError:
            continue
    with open('greek_marinas.txt','w') as file:
        for item in list_url:
            file.write(item + "\n")
#%%

