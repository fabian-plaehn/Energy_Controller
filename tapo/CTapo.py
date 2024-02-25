import time
#from PyP100 import PyP100
from hidden.hidden import tapo_email, tapo_password, tapo_ip_1, HIVE_API_KEY, FARM_NAME_B, FARM_NAME_H
from coins.Coins import coins
from HiveOS.HiveOS import Hive
from utils import logger


class Always_On_P100:
    def turn_on(self):
        return

    def turn_off(self):
        return

    def get_status(self):
        return True

    def getDeviceName(self):
        return "Dummy_P100"
    

import logging
from base64 import b64decode

from PyP100 import MeasureInterval

from .auth_protocol import AuthProtocol, OldProtocol

log = logging.getLogger(__name__)


class Device:
    def __init__(self, address, email, password, preferred_protocol=None, **kwargs):
        self.address = address
        self.email = email
        self.password = password
        self.kwargs = kwargs
        self.protocol = None
        self.preferred_protocol = preferred_protocol

    def _initialize(self):
        protocol_classes = {"new": AuthProtocol, "old": OldProtocol}

        # set preferred protocol if specified
        if self.preferred_protocol and self.preferred_protocol in protocol_classes:
            protocols_to_try = [protocol_classes[self.preferred_protocol]]
        else:
            protocols_to_try = list(protocol_classes.values())

        for protocol_class in protocols_to_try:
            if not self.protocol:
                try:
                    protocol = protocol_class(
                        self.address, self.email, self.password, **self.kwargs
                    )
                    protocol.Initialize()
                    self.protocol = protocol
                except:
                    logger.exception(f"Failed to initialize protocol {protocol_class.__name__}")
        if not self.protocol:
            raise Exception("Failed to initialize protocol")

    def request(self, method: str, params: dict = None):
        if not self.protocol:
            self._initialize()
        return self.protocol._request(method, params)

    def handshake(self):
        if not self.protocol:
            self._initialize()
        return

    def login(self):
        return self.handshake()

    def getDeviceInfo(self):
        return self.request("get_device_info")

    def _get_device_info(self):
        return self.request("get_device_info")

    def _set_device_info(self, params: dict):
        return self.request("set_device_info", params)

    def getDeviceName(self):
        data = self.getDeviceInfo()
        encodedName = data["nickname"]
        name = b64decode(encodedName)
        return name.decode("utf-8")

    def switch_with_delay(self, state, delay):
        return self.request(
            "add_countdown_rule",
            {
                "delay": int(delay),
                "desired_states": {"on": state},
                "enable": True,
                "remain": int(delay),
            },
        )


class Switchable(Device):
    def get_status(self) -> bool:
        return self._get_device_info()["device_on"]

    def set_status(self, status: bool):
        return self._set_device_info({"device_on": status})

    def turnOn(self):
        return self.set_status(True)

    def turnOff(self):
        return self.set_status(False)

    def toggleState(self):
        return self.set_status(not self.get_status())

    def turnOnWithDelay(self, delay):
        return self.switch_with_delay(True, delay)

    def turnOffWithDelay(self, delay):
        return self.switch_with_delay(False, delay)


class Metering(Device):
    def getEnergyUsage(self) -> dict:
        return self.request("get_energy_usage")

    def getEnergyData(self, start_timestamp: int, end_timestamp: int, interval: MeasureInterval) -> dict:
        """Hours are always ignored, start is rounded to midnight, first day of month or first of January based on interval"""
        return self.request("get_energy_data", {"start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "interval": interval.value})


class Color(Device):
    def setBrightness(self, brightness: int):
        return self._set_device_info({"brightness": brightness})

    def setColorTemp(self, color_temp: int):
        return self._set_device_info({"color_temp": color_temp})

    def setColor(self, hue, saturation):
        return self._set_device_info(
            {"color_temp": 0, "hue": hue, "saturation": saturation}
        )


class P100(Switchable):
    pass


class MiningStack:
    def __init__(self, number_pcs, ip, CHive: Hive, always_on_stacks=False, efficient_sheet=True):

        if always_on_stacks:
            logger("Always On Stacks", "info")
            self.p100 = Always_On_P100()
        else:
            self.p100 = P100(ip, tapo_email, tapo_password)
        self.name = self.p100.getDeviceName()
        print(self.name, ip)
        self.number_pcs = number_pcs
        self.time_turn_on = time.time()
        self.time_turn_off = time.time()
        self.watt = 0
        self.profit = 0
        self.watt_even = 0
        self.watt_efficient = 0
        self.efficient_watt_difference = 0
        self.efficient_sheet = efficient_sheet
        self.profit_coin = None
        self.efficient_coin = None
        self.CHive = CHive
        self.all_fs = self.CHive.get_all_fs()
        self.last_fs = 0
        self.always_on_stacks = always_on_stacks

    def turn_on(self):
        logger("Turning on" + str(self.p100.getDeviceName()), "info")
        self.p100.turnOn()
        self.time_turn_on = time.time()

    def turn_off(self):
        logger("Turning off" + str(self.p100.getDeviceName()), "info")
        self.p100.turnOff()
        self.time_turn_off = time.time()

    def update_coin(self):
        coins.sort(key=lambda x: x.profitability, reverse=True)
        print(coins)
        self.profit_coin = coins[0].name
        self.profit = coins[0].profitability * self.number_pcs
        self.watt = coins[0].watt * self.number_pcs * 1000

        coins.sort(key=lambda x: x.break_even_watt, reverse=True)
        print(coins)
        self.efficient_coin = coins[0].name
        self.watt_efficient = coins[0].watt * self.number_pcs * 1000
        self.watt_even = coins[0].break_even_watt * self.number_pcs

        self.efficient_watt_difference = self.watt - self.watt_efficient

    def get_status(self):
        return self.p100.get_status()

    def set_sheet(self):
        if not self.p100.get_status():
            return

        if self.efficient_sheet:
            logger(f"Set efficient Sheet {self.efficient_coin}", "info")
            fs = [fs for fs in self.all_fs if fs["name"] == self.efficient_coin][0]
        else:
            logger(f"Set profit Sheet {self.profit_coin}", "info")
            fs = [fs for fs in self.all_fs if fs["name"] == self.profit_coin][0]

        if fs["id"] != self.last_fs:
            logger("Set new flightsheet", "info")
            self.CHive.set_fs_all(fs["id"])
            self.last_fs = fs["id"]


Mining_Stack_01 = MiningStack(6, ip="192.168.0.100", CHive=Hive(token=HIVE_API_KEY, farm_name=FARM_NAME_H, available_worker_ids=[8395042, 8394783, 8436278, 8361530, 8397124, 8395108]))
time.sleep(1)

Mining_Stack_03 = MiningStack(6, ip="192.168.0.102", CHive=Hive(token=HIVE_API_KEY, farm_name=FARM_NAME_H, available_worker_ids=[8327057, 8395188, 8616656, 8395138, 8395190, 8436296]))
time.sleep(1)
Mining_Stack_02 = MiningStack(6, ip="192.168.0.101", CHive=Hive(token=HIVE_API_KEY, farm_name=FARM_NAME_H, available_worker_ids=[8319532, 8397123, 8307350, 8327018, 8327118,8317656]), always_on_stacks=True)
time.sleep(1)
Mining_Stack_04 = MiningStack(6, ip="192.168.0.100", CHive=Hive(token=HIVE_API_KEY, farm_name=FARM_NAME_B, available_worker_ids=None), always_on_stacks=False)

Mining_Stacks = [Mining_Stack_01, Mining_Stack_02,Mining_Stack_03,Mining_Stack_04]



