import time
from PyP100 import PyP100
from hidden import tapo_email, tapo_password, tapo_ip_1, HIVE_API_KEY, FARM_NAME_B, FARM_NAME_A
from coins.Coins import coins
from HiveOS.HiveOS import Hive
from utils import log


class Always_On_P100:
    def turn_on(self):
        return

    def turn_off(self):
        return

    def get_status(self):
        return True

    def getDeviceName(self):
        return "Dummy_P100"


class MiningStack:
    def __init__(self, number_pcs, ip, CHive: Hive, always_on_stacks=False):

        if always_on_stacks:
            log("Always On Stacks", "info")
            self.p100 = Always_On_P100()
        else:
            self.p100 = PyP100.P100(ip, tapo_email, tapo_password)
        self.name = self.p100.getDeviceName()

        self.number_pcs = number_pcs
        self.time_turn_on = time.time()
        self.time_turn_off = time.time()
        self.watt = 0
        self.profit = 0
        self.watt_even = 0
        self.watt_efficient = 0
        self.efficient_watt_difference = 0
        self.efficient_sheet = True
        self.profit_coin = None
        self.efficient_coin = None
        self.CHive = CHive
        self.all_fs = self.CHive.get_all_fs()
        self.last_fs = 0
        self.always_on_stacks = always_on_stacks

    def turn_on(self):
        log("Turning on" + str(self.p100.getDeviceName()), "info")
        self.p100.turnOn()
        self.time_turn_on = time.time()

    def turn_off(self):
        log("Turning off" + str(self.p100.getDeviceName()), "info")
        self.p100.turnOff()
        self.time_turn_off = time.time()

    def update_coin(self):
        for coin in coins:
            coin.get_profitability()
        coins.sort(key=lambda x: x.profitability, reverse=True)
        self.profit_coin = coins[0].name
        self.profit = coins[0].profitability * self.number_pcs
        self.watt = coins[0].watt * self.number_pcs

        coins.sort(key=lambda x: x.break_even_watt, reverse=True)
        print(coins)
        self.efficient_coin = coins[0].name
        self.watt_efficient = coins[0].watt * self.number_pcs
        self.watt_even = coins[0].break_even_watt * self.watt / 1000

        self.efficient_watt_difference = self.watt - self.watt_efficient

    def get_status(self):
        return self.p100.get_status()

    def set_sheet(self):
        if not self.p100.get_status():
            return

        if self.efficient_sheet:
            log("Set efficient Sheet", "info")
            print(self.efficient_coin)
            print([fs["name"] for fs in self.all_fs])
            fs = [fs for fs in self.all_fs if fs["name"] == self.efficient_coin][0]
        else:
            log("Set profit Sheet", "info")
            print(self.profit_coin)
            print([fs["name"] for fs in self.all_fs])
            fs = [fs for fs in self.all_fs if fs["name"] == self.profit_coin][0]

        if fs["id"] != self.last_fs:
            log("Set new flightsheet", "info")
            self.CHive.set_fs_all(fs["id"])
            self.last_fs = fs["id"]


Mining_Stack_01 = MiningStack(6, ip=tapo_ip_1, CHive=Hive(token=HIVE_API_KEY, farm_name=FARM_NAME_A, available_worker_ids=None), always_on_stacks=True)
Mining_Stack_02 = MiningStack(6, ip=tapo_ip_1, CHive=Hive(token=HIVE_API_KEY, farm_name=FARM_NAME_B, available_worker_ids=None), always_on_stacks=True)

Mining_Stacks = [Mining_Stack_01, Mining_Stack_02]



