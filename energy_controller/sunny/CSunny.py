import os
import sys
import time
from dataclasses import dataclass
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from energy_controller.hidden.hidden import sunny_username, sunny_password
from energy_controller.utils import telegram_bot_sendtext, Main_Restart_Exception

@dataclass
class EnergyData:
    pvpower: int
    feedin: int
    selfcsmp: int
    gridcsmp: int
    csmp: int
    batterypower: int
    batterystatus: int
    max_battery_power: int = 3900


class EnergyController:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://127.0.0.1:1880/ui/")
        time.sleep(3)
        self.max_btr_pwr = 3900
        
        self.bcharg_p = 0
        self.bdcharg_p = 0
        self.b_percent = 0
        self.grid_feed_p = 0
        self.csmp_p = 0
        
        self.adapt = 0.5
            
    def get_usable_power(self):
        try:
            self.bcharg_p = self.bcharg_p * self.adapt + self.adapt * float(self.driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[5]/div/div/md-card[1]/p[2]').text.split(" ")[0])  # x W bcharing_power
            self.bdcharg_p = self.bdcharg_p * self.adapt + self.adapt * float(self.driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[5]/div/div/md-card[2]/p[2]').text.split(" ")[0])
            self.b_percent = float(self.driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[5]/div/div/md-card[3]/p[2]').text.split(" ")[0])
            self.grid_feed_p = self.grid_feed_p * self.adapt + self.adapt * float(self.driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[1]/div/div/md-card[1]/p[2]').text.split(" ")[0])
            self.csmp_p = self.csmp_p * self.adapt + self.adapt * float(self.driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[1]/div/div/md-card[2]/p[2]').text.split(" ")[0])

            net_pwr = self.bcharg_p - self.bdcharg_p + self.grid_feed_p - self.csmp_p
            
            if net_pwr > 0:
                return net_pwr
            
            # if battery max power is exceed fall down always
            if abs(net_pwr) > self.max_btr_pwr:  
                return self.max_btr_pwr - abs(net_pwr)
            
            # if battery is nicely charged and b_pwr not exceed give some energy
            if self.b_percent > 60:
                return max(self.max_btr_pwr - self.bdcharg_p-500, 0)
            
            if self.b_percent > 20:
                return 0
            
            return net_pwr
        except NoSuchElementException:
            return 0

    def reset(self):
        self.__init__()


if __name__ == "__main__":
    test_C = EnergyController()
    for _ in range(5):
        for i in range(5):
            print(test_C.get_usable_power())
            time.sleep(1)
        test_C.reset()


