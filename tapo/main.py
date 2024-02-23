import time

from PyP100 import PyP100
from hidden import tapo_email, tapo_password



p100 = PyP100.P100("192.168.178.146", tapo_email, tapo_password)

#pip install git+https://github.com/almottier/TapoP100.git@main
#62.226.73.154:13337
#pip install git+https://github.com/almottier/TapoP100.git@main

p100.turnOff()
time.sleep(2)
p100.turnOn()
time.sleep(2)
p100.turnOff()
