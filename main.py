import time
from dataclasses import dataclass, asdict
from PyP100 import PyP100
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from hidden import username, password

@dataclass
class EnergyData:
    pvpower: int
    feedin: int
    selfcsmp: int
    gridcsmp: int
    csmp: int
    batterypower: int
    batterystatus: int


def main():
    driver = webdriver.Firefox()
    driver.get("https://www.sunnyportal.com/Templates/Start.aspx?ReturnUrl=%2fFixedPages%2fDashboard.aspx")


    ## LOGIN ##
    WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
    driver.find_element(By.ID, "txtUserName").send_keys(username)
    driver.find_element(By.ID, "txtPassword").send_keys(password)
    time.sleep(1)
    WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Logincontrol1_LoginBtn"))).click()
    WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div[2]/table/tbody/tr[2]/td[1]/a"))).click()

    while True:
        try:
            pvpower = int(driver.find_element(by=By.ID, value='pvpower').text.split(" ")[0].replace(",", "."))
            feedin = int(driver.find_element(by=By.ID, value='feedin').text.split(" ")[0].replace(",", "."))
            selfcsmp = int(driver.find_element(by=By.ID, value='selfcsmp').text.split(" ")[0].replace(",", "."))
            gridcsmp = int(driver.find_element(by=By.ID, value='gridcsmp').text.split(" ")[0].replace(",", "."))
            csmp = int(driver.find_element(by=By.ID, value='csmp').text.split(" ")[0].replace(",", "."))

            batterypower = int(driver.find_element(by=By.ID, value='ctl00_ContentPlaceHolder1_SelfConsumption_Status1_BatteryPower').text.split(" ")[0])
            batterystatus = int(driver.find_element(by=By.ID, value='ctl00_ContentPlaceHolder1_SelfConsumption_Status1_BatteryChargeStatus').text.split(" ")[0])

            energy_data = EnergyData(pvpower, feedin, selfcsmp, gridcsmp, csmp, batterypower, batterystatus)
            print(energy_data)
            time.sleep(5)
        except ValueError:
            pass


if __name__ == '__main__':
    main()


