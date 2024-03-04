import datetime
import json
import os
import sys
import time
import urllib.request
import pandas as pd
from pycoingecko import CoinGeckoAPI
import requests
from requests import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd
from hidden.hidden import bot_chatID, bot_token


def append_row(df, row):
    return pd.concat([
                df, 
                pd.DataFrame([row], columns=row.index)]
           ).reset_index(drop=True)
            

def telegram_bot_sendtext(bot_message : str):
    bot_message = bot_message.replace("_", "")
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

Watt_Costs_Own = 0.08
Watt_Costs_All_In = 0.4
letter_factor = {"k": 1e3, "m": 1e6, "g": 1e9}


#  "Data provided by CoinGecko"

class CoinStatsBase:
    def __init__(self):
        self.difficulty = None
        self.network_hashrate = None
        self.price = 0
        self.last_price_update = time.time()
        self.price_update = 2 * 60 * 60
        self.block_reward = 12.5
        self.hashrate = 11500
        self.watt = 0.115
        self.profitability = 0
        self.profit_per_watt = 0
        self.revenue = 0
        self.break_even_watt = 0
        self.name = ""
        self.cg = CoinGeckoAPI()
        self.cg.api_base_url = 'https://api.coingecko.com/api/v3/'
        self.hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.xeggex_ticker = None
        self.market = None
        self.cg_id = None

    def get_difficulty(self):
        pass

    def get_price(self):
        import yfinance as yf
        if self.price != 0 and (time.time() - self.last_price_update) < self.price_update:
            return

        if self.market == "coingecko":
            try:
                ohlc = self.cg.get_coin_ohlc_by_id(id=self.cg_id, vs_currency="eur", days="1")
                df = pd.DataFrame(ohlc)
                df.columns = ["date", "open", "high", "low", "close"]
                df["date"] = pd.to_datetime(df["date"], unit="ms")
                df.set_index("date", inplace=True)
                self.price = df["close"].iloc[-1]  # .mean()
                
            except requests.exceptions.InvalidHeader:
                print("invalid header")
                return
        if self.market == "xeggex":
            try:
                #response = request("GET", f'https://api.xeggex.com/api/v2/market/candles?symbol={self.xeggex_ticker}%2FUSDT&from={time.time() - 60 * 60 * 24}&to={time.time()}&resolution=60&countBack=24&firstDataRequest=1')
                price = 0
                response = request("GET", f"https://api.xeggex.com/api/v2/market/getbysymbol/{self.xeggex_ticker}%2FUSDT")
                price = float(response.json()["lastPrice"])
                usd2eur = yf.download(tickers = 'USDEUR=X', period ='1d', interval = '15m', progress=False)
                self.price = price * usd2eur["Close"].iloc[-1]
                
                try:
                    df = pd.read_csv(f"dataset/USD.txt")
                except FileNotFoundError:
                    with open(f"dataset/USD.txt", "w") as f:
                        f.write(f"Time,USD_Price[EUR]")
                    df = pd.read_csv(f"dataset/USD.txt")
                date_now = datetime.datetime.now().strftime("%d/%m/%Y")
                if date_now not in list(df["Time"]):
                    new_row = pd.Series({"Time":date_now, f"USD_Price[EUR]":usd2eur["Close"].iloc[-1]})
                    df = append_row(df, new_row)
                else:
                    df[f"USD_Price[EUR]"][(df["Time"] == date_now)] = usd2eur["Close"].iloc[-1]
                df.to_csv(f"dataset/USD.txt", sep=",", index=False)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                telegram_bot_sendtext("crashed in coins")
                telegram_bot_sendtext(f"{exc_type, fname, exc_tb.tb_lineno}")  
                pass
            
        if self.price != 0:
            self.last_price_update = time.time()
            try:
                df = pd.read_csv(f"dataset/{self.name}.txt")
            except FileNotFoundError:
                with open(f"dataset/{self.name}.txt", "w") as f:
                    f.write(f"Time,{self.name}_Price[EUR]")
                df = pd.read_csv(f"dataset/{self.name}.txt")
            date_now = datetime.datetime.now().strftime("%d/%m/%Y")
            if date_now not in list(df["Time"]):
                new_row = pd.Series({"Time":date_now, f"{self.name}_Price[EUR]":self.price})
                df = append_row(df, new_row)
            else:
                df[f"{self.name}_Price[EUR]"][(df["Time"] == date_now)] = self.price
            df.to_csv(f"dataset/{self.name}.txt", sep=",", index=False)

    def get_profitability(self):
        self.get_difficulty()
        self.get_price()

        if self.price is None or self.difficulty is None:
            self.price = 0
            blocks_per_second = 0
        else:
            blocks_per_second = self.hashrate / self.difficulty
        rev_per_day = 60 * 60 * 24 * blocks_per_second * self.block_reward * self.price

        profit_watt_own = rev_per_day - self.watt * 24 * Watt_Costs_Own  # kW W
        profit_watt_all_in = rev_per_day - self.watt * 24 * Watt_Costs_All_In  # kW W
        break_even_watt_costs = rev_per_day / (self.watt * 24)
        # print(f"{self.name}, rev: {rev_per_day}, watt_own: {profit_watt_own}, watt_all: {profit_watt_all_in}, break_even: {break_even_watt_costs}")
        self.profitability = profit_watt_own
        self.profit_per_watt = self.profitability / self.watt
        self.revenue = rev_per_day
        self.break_even_watt = break_even_watt_costs


def find_text(text, text_to_find):
    value = None
    text = " ".join(str(text).split())

    idx = text.find(text_to_find)
    start = idx + len(text_to_find)
    i = 1

    for i in range(1, 15):
        try:
            value = float(text[start:start + i].replace(",", ""))
        except ValueError:
            break
    return value, text, start, i


class YDAStats(CoinStatsBase):
    def __init__(self):
        super(YDAStats, self).__init__()
        self.hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.difficulty = None
        self.price = None
        self.block_reward = 11.25
        self.hashrate = 12000
        self.watt = 0.120
        self.name = "YDA"
        self.cg_id = 'yadacoin'
        self.xeggex_ticker = "YDA"
        self.market = "xeggex"
        self.driver = webdriver.Firefox()
            

    def get_difficulty(self):
        self.driver.get("https://yadacoin.io/explorer")
        #WebDriverWait(self.driver, 5).until(ec.((By.XPATH, "/html/body/main/div/section/div/app-root/app-search-form/h3[3]")))
        for _ in range(15):
            difficulty = find_text(self.driver.find_element(by=By.XPATH, value="/html/body/main/div/section/div/app-root/app-search-form/h3[3]").text, "Difficulty: ")[0]
            if difficulty is not None:
                self.difficulty = difficulty
                break
            time.sleep(3)
        



class AVN_Stats(CoinStatsBase):
    def __init__(self):
        super(AVN_Stats, self).__init__()
        self.hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.difficulty = None
        self.price = None
        self.block_reward = 1187.50
        self.block_time = 30
        self.hashrate = 13000
        self.watt = 0.105
        self.name = "AVN"
        self.cg_id = "avian-network"

    def get_difficulty(self):
        self.difficulty, text, start, i = find_text("https://blockexplorer.avn.network/", 'label id="hashrateMinx">')
        # print(self.difficulty)
        letter = text[start + i].lower()
        # print(self.difficulty, letter)
        self.difficulty *= letter_factor[letter] * self.block_time
        # print(self.difficulty)

    def get_price(self):
        self.price, _, _, _ = find_text("https://xeggex.com/market/AVN_USDT",
                                        'class="marketlastprice" style="font-family: XeggexPlex, Arial, sans-serif !important;">')


#  LmN3Jys8vo4JeRzKaxhbk5BAYKrDs4j1H
class XDAG_Stats(CoinStatsBase):
    def __init__(self):
        super(XDAG_Stats, self).__init__()
        self.hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.difficulty = None
        self.price = None
        self.block_reward = 64
        self.block_time = 64
        self.hashrate = 12000
        self.watt = 0.120
        self.name = "XDAG"
        self.cg_id = "dagger"
        self.market = "coingecko"

    def get_difficulty(self):
        try:
            with urllib.request.urlopen("https://explorer.xdag.io/api/status") as url:
                data = json.load(url)
                self.network_hashrate = data["stats"]['hashrate'][1]
        except:
            print("fucking site down xdag")
            if self.network_hashrate is None:
                self.network_hashrate = 2_000_000_000
        self.difficulty = self.network_hashrate * self.block_time


class ZEPH_Stats(CoinStatsBase):
    def __init__(self):
        super(ZEPH_Stats, self).__init__()
        self.hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.difficulty = None
        self.price = None
        self.block_reward = 10.7
        self.block_time = 120
        self.hashrate = 12000
        self.watt = 0.12
        self.name = "ZEPH"
        self.cg_id = "zephyr-protocol"
        self.market = "coingecko"

    def get_difficulty(self):
        try:
            with urllib.request.urlopen("https://explorer.zephyrprotocol.com/") as url:
                string = url.read().decode('utf-8')
                self.difficulty = find_text(string, "difficulty: ")[0]
                self.network_hashrate, text, start, i = find_text(string, "Hash rate: ")
                letter = text[start + i - 1].lower()
                self.network_hashrate *= letter_factor[letter]
        except:
            print("fucking site down zeph")
            if self.network_hashrate is None:
                self.network_hashrate = 2_500_000_000
            self.difficulty = self.network_hashrate * self.block_time


class RTC_Stats(CoinStatsBase):
    def __init__(self):
        super(RTC_Stats, self).__init__()

        self.difficulty = None
        self.price = None

        self.block_reward = 3750
        self.hashrate = 3200
        self.block_time = 120
        self.watt = 0.095
        self.name = "RTC"
        self.cg_id = "reaction"
        self.market = "xeggex"
        self.xeggex_ticker = "RTC"

    def get_difficulty(self):
        try:
            with urllib.request.urlopen("https://explorer.reaction.network/api/getnetworkhashps") as url:
                self.network_hashrate = json.load(url)
        except:
            print("fucking site down rtc")
            if self.network_hashrate is None:
                self.network_hashrate = 9999999999999
        self.difficulty = self.network_hashrate * self.block_time

#192.168.178.147
class VishAIStats(CoinStatsBase):
    def __init__(self):
        super(VishAIStats, self).__init__()
        self.block_reward = 2571.6
        self.hashrate = 2200
        self.block_time = 60
        self.watt = 0.095
        self.name = "VishAI"
        self.market = "xeggex"
        self.xeggex_ticker = "VISH"

    def get_difficulty(self):
        try:
            req = urllib.request.Request("https://explorer.vishcoin.com/api/getnetworkhashps", headers=self.hdr)
            with urllib.request.urlopen(req) as url:
                self.network_hashrate = json.load(url)
        except:
            self.network_hashrate = 33_000_000
        self.difficulty = self.network_hashrate * self.block_time


rtc = RTC_Stats()
xdag = XDAG_Stats()
zeph = ZEPH_Stats()
avn = AVN_Stats()
yada = YDAStats()
vishai = VishAIStats()

coins = [rtc, xdag, zeph, yada]

if __name__ == "__main__":
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib.request.Request("https://explorer.vishcoin.com/api/getnetworkhashps", headers=hdr)
    # with urllib.request.urlopen(req) as url:
    #    string = json.load(url)
    # print(string)
    coins = [rtc, xdag, zeph, yada]

    for coin in coins:
        coin.get_profitability()
        print(coin.name, coin.revenue, coin.profitability, coin.break_even_watt, coin.price, coin.network_hashrate, coin.difficulty)
