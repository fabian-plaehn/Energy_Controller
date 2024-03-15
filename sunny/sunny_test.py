from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
driver = webdriver.Firefox()

driver.get("http://127.0.0.1:1880/ui/")

while True:
    try:
        bcharg_p = driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[5]/div/div/md-card[1]/p[2]').text.split(" ")[0]  # x W bcharing_power
        bdcharg_p = driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[5]/div/div/md-card[2]/p[2]').text.split(" ")[0]
        b_percent = driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[5]/div/div/md-card[3]/p[2]').text.split(" ")[0]
        grid_feed_p = driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[1]/div/div/md-card[1]/p[2]').text.split(" ")[0]
        csmp_p = driver.find_element(by=By.XPATH, value='/html/body/md-content/section/md-content/div[1]/ui-card-panel[1]/div/div/md-card[2]/p[2]').text.split(" ")[0]

        print(f"B_CHARGE: {bcharg_p}, B_DISCHARGE: {bdcharg_p}, B_PERCENT: {b_percent}, GRID_FEED: {grid_feed_p}, CSM_P: {csmp_p}")
    
    except:
        print("not found") 
    time.sleep(1)
    