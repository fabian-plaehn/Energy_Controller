import os
import sys
import time
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from hidden.hidden import sunny_username, sunny_password

@dataclass
class EnergyData:
    pvpower: int
    feedin: int
    selfcsmp: int
    gridcsmp: int
    csmp: int
    batterypower: int
    batterystatus: int
    max_battery_power: int = 4000


class EnergyController:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get("https://www.sunnyportal.com/Templates/Start.aspx?ReturnUrl=%2fFixedPages%2fDashboard.aspx")

        ## LOGIN ##
        WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
        self.driver.find_element(By.ID, "txtUserName").send_keys(sunny_username)
        self.driver.find_element(By.ID, "txtPassword").send_keys(sunny_password)
        time.sleep(1)
        WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Logincontrol1_LoginBtn"))).click()
        WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div[2]/table/tbody/tr[2]/td[1]/a"))).click()  # FARM SPECIFIC

    def get_data(self):
        try:
            pvpower = int(self.driver.find_element(by=By.ID, value='pvpower').text.split(" ")[0].replace(",", ".").replace(" ", ""))
            feedin =  0  # int(self.driver.find_element(by=By.ID, value='feedin').text.split(" ")[0].replace(",", ".").replace(" ", ""))
            selfcsmp = 0 # int(self.driver.find_element(by=By.ID, value='selfcsmp').text.split(" ")[0].replace(",", ".").replace(" ", ""))
            gridcsmp = 0  # int(self.driver.find_element(by=By.ID, value='gridcsmp').text.split(" ")[0].replace(",", ".").replace(" ", ""))
            csmp = int(self.driver.find_element(by=By.ID, value='csmp').text.split(" ")[0].replace(",", ".").replace(" ", ""))

            batterypower = 0  # int(self.driver.find_element(by=By.ID, value='ctl00_ContentPlaceHolder1_SelfConsumption_Status1_BatteryPower').text.split(" ")[0])
            batterystatus = int(self.driver.find_element(by=By.ID, value='ctl00_ContentPlaceHolder1_SelfConsumption_Status1_BatteryChargeStatus').text.split(" ")[0])

            energy_data = EnergyData(pvpower, feedin, selfcsmp, gridcsmp, csmp, batterypower, batterystatus)
            return energy_data
        except ValueError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return None


if __name__ == "__main__":
    test_C = EnergyController()
    while True:
        print(test_C.get_data())
        time.sleep(5)


