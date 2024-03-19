import time
#from PyP100 import PyP100

sunny_username = "elke.plaehn@t-online.de"
sunny_password = "Sunny,.-0947"

tapo_email = "fabianplaehn28+tp@gmail.com"
tapo_password = "JvSbru!NN8sl@6V"

HIVE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3MTEwZTIyMi02ZGM2LTQ4MmYtOGE1OS0wOTcwYmQ2NjdkZGQifQ.eyJleHAiOjIwMTc5MzQ1MDYsIm5iZiI6MTcwMjMxNTMwNiwiaWF0IjoxNzAyMzE1MzA2LCJqdGkiOiI2ZWY0MTA4ZS0xMGQ0LTQ2MzUtYTBjYi1mNWU0YmVjMTJiOGEiLCJzdWIiOiI2ZWY0MTA4ZS0xMGQ0LTQ2MzUtYTBjYi1mNWU0YmVjMTJiOGEifQ.njpgRvxvASFbLnGY3eSJ4rZ4XoO4hFWomX_s-Rmk-qM"
FARM_NAME_B = "B_Farm"
FARM_NAME_H = "H_Farm"

WALLET_RTC = {"B_FARM":"Rbich3z6HinDYFgmtm1ZhZzkxWLoghrgAX",
              "H_FARM":"RfSWwwitXvc4h1uaWUrzyizjfRBWSsnEEB"}

WALLET_ZEPH = {"B_FARM":"ZEPHYR2LgDTLQLdNi2hhLF57xz12wNhaeNtGXSkGjAF8bYx7R2wfgAyBi6VKbNAAL4MMz5sHbFU2gZE2sd5qn8CoKz21PHw2Ekk4V", 
               "H_FARM":"ZEPHYR2Kur2T72QpzZRqpBRAHXhRT6TLsV2GibYHpubiZYWUpC39gFDW8GYZ9ev4Bd5T7xZN96TWH9ZwZkQ5qRwgKkWBwSsFZRP41"}

WALLET_XDAG = {"B_FARM":"Joi7vhWjXDs4HzpmMgVFYvLL6KJHyguxr",
               "H_FARM":"C9vpePe8VCrHqSjDZedSNjNMBCEMipNjA"}

WALLET_YADA = {"B_FARM":"18ogVSRVT8dSoWBFzCUWf7a2uqtckMHhwh",
               "H_FARM":"1BGwDCCiBDggWeZJNJDYHqyCnDMniSfB34"}

WALLET_QUBIC = {"B_FARM": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJJZCI6IjY0ZTdmNzIyLTA1ZDgtNDNlYy05YTU0LTBlNTljMGUzMGRjOSIsIk1pbmluZyI6IiIsIm5iZiI6MTcxMDczNjE3OCwiZXhwIjoxNzQyMjcyMTc4LCJpYXQiOjE3MTA3MzYxNzgsImlzcyI6Imh0dHBzOi8vcXViaWMubGkvIiwiYXVkIjoiaHR0cHM6Ly9xdWJpYy5saS8ifQ.ocEImMk5ryDSRvubZSSEoD3Wi58y4H5v76vsowuExAKdrLBqgqedta9lzWOx8M5ANkXrd20Zye6g3Hw5Yk9rDQ",
                "H_FARM": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJJZCI6ImUzNDQ0M2Y2LWFjM2MtNGFmNy1hNWY2LWE2NDY3Yjc1NmVjOSIsIk1pbmluZyI6IiIsIm5iZiI6MTcxMDczNDg3OSwiZXhwIjoxNzQyMjcwODc5LCJpYXQiOjE3MTA3MzQ4NzksImlzcyI6Imh0dHBzOi8vcXViaWMubGkvIiwiYXVkIjoiaHR0cHM6Ly9xdWJpYy5saS8ifQ.XP_pueBSUKoHduWT3ddXCDNPY1g6Gr_YeUPCI1_0UqgjEoHaTtp7ndPoC9QLz566txsGVG71KlYBnR2VjHimxg"}

xmrig_server_ip = "100.96.102.113:3344"
# pip install git+https://github.com/almottier/TapoP100.git@main
# 62.226.73.154:13337
tapo_ip_1 = "192.168.178.146"
# pip install git+https://github.com/almottier/TapoP100.git@main
'''p100 = PyP100.P100("62.226.73.154:13337", tapo_email, tapo_password)

print(p100.get_status())
p100.turnOff()
print(p100.get_status())
time.sleep(2)
p100.turnOn()
print(p100.get_status())
time.sleep(2)
p100.turnOff()'''
