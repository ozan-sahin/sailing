import bs4 as bs
import requests
import pandas as pd
import datetime

# MAX_LENGTH = "25"
# PRICE_MAX = ""
# YEAR_MIN = "2010"

def parse(YEAR_MIN : str = "2010", PRICE_MAX : str = "", MAX_LENGTH : str = "25"):

  headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Accept-Language': 'en-US,en;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br'}

  #Scraping all the pages from theyachtmarket.com

  url = f"https://www.theyachtmarket.com/en/boats-for-sale/search/?neworused=used&currency=eur&"+ \
  f"lengthunit=metres&boattypeids=272&showsail=1&"+ \
  f"&priceto={PRICE_MAX}&lengthto={MAX_LENGTH}&yearfrom={YEAR_MIN}"

  #Find last page
  r = requests.get(url, headers=headers)

  # Run it on https://colab.research.google.com/ - otherwise IP gets blocked 🤨
  soup = bs.BeautifulSoup(r.text, "lxml")
  results_count = soup.find("small")
  last_page = int(results_count.text.split()[0].replace("(","").replace(",",""))
  final_list = []

  for page in range(1,last_page+1):
    
      url = f"https://www.theyachtmarket.com/en/boats-for-sale/search/?neworused=used&currency=eur&"+ \
      f"lengthunit=metres&boattypeids=272&showsail=1&"+ \
      f"&priceto={PRICE_MAX}&lengthto={MAX_LENGTH}&yearfrom={YEAR_MIN}&page={str(page)}"

      r = requests.get(url, headers=headers)
      soup = bs.BeautifulSoup(r.text, "lxml")

      for ad in soup.findAll("div", {"class" : "row result"}):

          title = ad.find("a" , {"class" : "boat-name"}).text
          link = "https://www.theyachtmarket.com" + ad.find("a" , {"class" : "boat-name"}).get("href")
          location = ad.find("div", {"class" : "location"}).text
          price = ad.find("div" , {"class" : "pricing"}).find("span").text
          specs = ad.find("div" , {"class" : "overview"}).text.split("|")

          final_list.append({"Title" : title, "URL" : link, "Price" : price,
                            "Specs" : specs,"Location" : location}) 

  df = pd.DataFrame(final_list)
  df = clean(df)
  return df

def clean(df):
  df = df[~df["Price"].str.contains("POA")]
  df = df[df['Specs'].notna()]
  df["Title"] = df["Title"].apply(lambda x: x.capitalize())
  df["Price"] = df["Price"].apply(lambda x: x.split()[0].replace(",","").replace("€","")).astype(float)
  df["Model"] = df["Title"].apply(lambda x: x.split(" ")[0].strip())
  df[['Year Built', 'Length', "Engine", "Type", "Status"]] = pd.DataFrame(df["Specs"].to_list(), columns=['Year Built', 'Length', "Engine", "Type", "Status"])
  df['Length'] = df['Length'].apply(lambda x: x.strip().replace("m", "")).astype(float)
  df['Engine'] = df['Engine'].apply(lambda x: x.strip()).replace({'Sail': None})
  df[~df["Status"].notna()]
  df['Year Built'] = df['Year Built'].astype(float)
  df["Age"] = datetime.datetime.now().year - df["Year Built"]
  df["Source"] = "theyachtmarket"
  df["Query_Date"] = datetime.date.today()
  df = df.drop(['Specs', "Type", "Status"], axis=1)
  return df