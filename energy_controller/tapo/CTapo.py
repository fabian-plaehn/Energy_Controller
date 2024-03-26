import os
import sys
import time
#from PyP100 import PyP100
from energy_controller.hidden.hidden import tapo_email, tapo_password, tapo_ip_1, HIVE_API_KEY, FARM_NAME_B, FARM_NAME_H
from energy_controller.utils import logger, telegram_bot_sendtext
from energy_controller.my_mining_cc.mining_cc import Cxmrig

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



class P100(Switchable):
    pass


class MiningStack:
    def __init__(self, number_pcs, ip, CHive: Cxmrig, always_on_stacks=False, efficient_sheet=True, always_profit=False, always_efficient=False):

        if always_on_stacks:
            logger("Always On Stacks", "info")
            self.p100 = Always_On_P100()
        else:
            self.p100 = P100(ip, tapo_email, tapo_password)
        self.name = self.p100.getDeviceName()
        #print(self.name, ip, self.p100.get_status())
        self.number_pcs = number_pcs
        self.time_turn_on = time.time()
        self.time_turn_off = time.time()
        self.watt = 0
        self.profit = 0
        self.even_watt_rate = 0
        self.watt_efficient = 0
        self.efficient_watt_difference = 0
        self.efficient_sheet = efficient_sheet
        self.profit_coin = None
        self.efficient_coin = None
        self.CHive = CHive
        
        #self.all_fs = self.CHive.get_all_fs()
        self.last_fs = 0
        self.always_on_stacks = always_on_stacks
        self.always_profit = always_profit
        self.always_efficient = always_efficient
        
        self.current_coin = None
        self.current_watt = 0
        self.current_revenue = 0
        self.set_sheet_time = time.time()

    def turn_on(self):
        logger("Turning on" + str(self.p100.getDeviceName()), "info")
        self.p100.turnOn()
        self.time_turn_on = time.time()

    def turn_off(self):
        logger("Turning off" + str(self.p100.getDeviceName()), "info")
        self.p100.turnOff()
        self.time_turn_off = time.time()

    def update_coin(self, coins):
        coins.sort(key=lambda x: x.profitability, reverse=True)
        self.profit_coin = coins[0].name
        self.revenue_profit = coins[0].revenue * self.number_pcs
        self.profit = coins[0].profitability * self.number_pcs
        self.watt = coins[0].watt * self.number_pcs * 1000

        coins.sort(key=lambda x: x.break_even_watt, reverse=True)
        self.efficient_coin = coins[0].name
        self.revenue_efficient = coins[0].revenue * self.number_pcs
        self.watt_efficient = coins[0].watt * self.number_pcs * 1000
        self.even_watt_rate = coins[0].break_even_watt * self.number_pcs

        self.efficient_watt_difference = self.watt - self.watt_efficient

    def get_status(self):
        return self.p100.get_status()

    def set_sheet(self):
        self.set_sheet_time = time.time()
        try:
            if (self.efficient_sheet or self.always_efficient) and not self.always_profit:
                self.CHive.set_sheet(self.efficient_coin)
                self.current_coin = self.efficient_coin
                self.current_watt = self.watt_efficient
                self.current_revenue = self.revenue_efficient
                logger(f"Set efficient flightsheet {self.efficient_coin}", "info")
                telegram_bot_sendtext(f"Set efficient flightsheet {self.efficient_coin}")
            else:
                self.CHive.set_sheet(self.profit_coin)
                self.current_coin = self.profit_coin
                self.current_watt = self.watt
                self.current_revenue = self.revenue_profit
                telegram_bot_sendtext(f"Set profit flightsheet {self.profit_coin}")
                logger(f"Set profit flightsheet {self.profit_coin}", "info")
            
        except KeyError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            telegram_bot_sendtext("crashed in CTapo set_sheet")
            telegram_bot_sendtext(f"{exc_type, fname, exc_tb.tb_lineno}")
            
        
    def __repr__(self) -> str:
        return f"[{self.p100.getDeviceName()}, {self.number_pcs}, {self.get_status()}]"
        
    #def __str__(self) -> str:
    #    return f"[{self.name}, {self.number_pcs}, {self.get_status()}]"

# Dose 1 2
Mining_Stack_01 = MiningStack(6, ip="192.168.178.32", CHive=Cxmrig("B_FARM", ["rig1C76F3", "rig1C771C", "rig416783", "rig6F61CF", "rigC49613", "rigC4961B"]), always_on_stacks=True)

# Dose 1 1
Mining_Stack_03 = MiningStack(6, ip="192.168.178.33", CHive=Cxmrig("B_FARM", ["rig3C086A", "rig3C08D6", "rig40B92F", "rig40B93D", "rigD3ABE7", "rigD3ABF1"]), always_on_stacks=True)

# Dose 2 1
Mining_Stack_02 = MiningStack(4, ip="192.168.178.34", CHive=Cxmrig("B_FARM", ["rig0040DF", "rig039E17", "rig1D1864", "rig7C4414"]), always_on_stacks=True)

# Dose 2 2
Mining_Stack_04 = MiningStack(3, ip="192.168.178.31", CHive=Cxmrig("B_FARM", ["rig3C08AB", "rig3C08BA", "rigC4959E"]), always_on_stacks=True)

Mining_Stack_05 = MiningStack(8, ip="192.168.0.100", CHive=Cxmrig("H_FARM", ["rig0ED8D9", "rig5E6D1A", "rig12FCF8", "rig12FD7E", "rig40B8E1", "rig40B93E", "rig40B966", "rig39527C"]), always_on_stacks=True, always_profit=True)

#8ab missing


Mining_Stacks = [Mining_Stack_01, Mining_Stack_02, Mining_Stack_03, Mining_Stack_04, Mining_Stack_05]


