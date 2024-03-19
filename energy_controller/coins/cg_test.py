import pandas as pd
from pycoingecko import CoinGeckoAPI
import requests
import yfinance as yf
import datetime

'''data = yf.download(tickers = 'USDEUR=X' ,period ='1d', interval = '15m')

print(data["Close"].iloc[-1])'''

cg = CoinGeckoAPI()
ohlc = cg.get_coin_ohlc_by_id(id="tether", vs_currency="eur", days="1")
df = pd.DataFrame(ohlc)
df.columns = ["date", "open", "high", "low", "close"]
df["date"] = pd.to_datetime(df["date"], unit="ms")
df.set_index("date", inplace=True)
price = df["close"].iloc[-1]  # .mean()
print(price)