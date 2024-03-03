import pandas as pd
from pycoingecko import CoinGeckoAPI
import requests
import yfinance as yf
import datetime

'''data = yf.download(tickers = 'USDEUR=X' ,period ='1d', interval = '15m')

print(data["Close"].iloc[-1])'''

xeggex_ticker = "RTC"

price = 0
response = requests.request("GET", f"https://api.xeggex.com/api/v2/market/getbysymbol/{xeggex_ticker}%2FUSDT")
price = float(response.json()["lastPrice"])
print(price)
usd2eur = yf.download(tickers = 'USDEUR=X' ,period ='1d', interval = '15m', progress=False)
price = price * usd2eur["Close"].iloc[-1]
print(price)  
                
def append_row(df, row):
    return pd.concat([
                df, 
                pd.DataFrame([row], columns=row.index)]
           ).reset_index(drop=True)
    
df = pd.read_csv("coins/test_file.txt")
date_now = datetime.datetime.now().strftime("%d/%m/%Y")
print(list(df["Time"]))
if date_now not in list(df["Time"]):
    new_row = pd.Series({"Time":date_now, "Zeph_Price[EUR]":20})
    df = append_row(df, new_row)
    print(df)
else:
    df["Zeph_Price[EUR]"][(df["Time"] == date_now)] = 10
    print(df)
    print("already there")
    
df.to_csv("coins/test_file.txt", sep=",", index=False)


#print(datetime.datetime.now().strftime("%d/%m/%Y"))