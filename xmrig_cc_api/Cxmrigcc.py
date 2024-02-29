import requests
import json
from hidden.hidden import WALLET_RTC, WALLET_ZEPH, WALLET_XDAG, WALLET_YADA, xmrig_server_ip


class Sheet:
    def __init__(self, coin_name, pool, user, algo=None, password=None) -> None:
        self.name = coin_name
        self.algo = algo
        self.pool = pool
        self.user = user
        self.password = password
        

rtc = Sheet(coin_name="RTC", algo="ghostrider", pool="stratum-eu.rplant.xyz:7054", user=WALLET_RTC, password="m=solo")
zeph = Sheet(coin_name="ZEPH", algo=None, pool="de.zephyr.herominers.com:1123", user=WALLET_ZEPH)
xdag = Sheet(coin_name="XDAG", algo="rx/xdag", pool="stratum.xdag.org:23655", user=WALLET_XDAG)
yada = Sheet(coin_name="YADA", algo="rx/yada", pool="yada.steadnet.net:3333", user=WALLET_YADA)

Sheets = [rtc, zeph, xdag, yada]

class Cxmrig:
    def __init__(self, farm_name, worker_ids) -> None:
        self.farm_name = farm_name
        self.worker_ids = worker_ids
        
    def set_sheet(self, name):
        sheet = [sheet for sheet in Sheets if sheet.name == name][0]
        api_url = f"http://admin:pass@{xmrig_server_ip}/admin/getClientConfig?clientId=template_BASE"
        response = requests.get(api_url)
        print(response)
        base_sheet = response.json()
        for worker_id in self.worker_ids:
            base_sheet["pools"][0]["algo"] = sheet.algo
            base_sheet["pools"][0]["url"] = sheet.pool
            base_sheet["pools"][0]["user"] = f"{sheet.user[self.farm_name]}"
            base_sheet["pools"][0]["pass"] = sheet.password
            

            api_url = f"http://admin:pass@{xmrig_server_ip}/admin/setClientConfig?clientId={worker_id}"
            headers = {"Content-Type":"application/json"}
            response = requests.post(api_url, headers=headers, json=base_sheet)
            print(response)
    
            api_url = f"http://admin:pass@{xmrig_server_ip}/admin/setClientCommand?clientId={worker_id}"
            headers = {"Content-Type":"application/json"}
            response = requests.post(api_url, headers=headers, json={"control_command":{"command":"UPDATE_CONFIG"}})
            print(response)
    
    
if __name__ == "__main__":
    xmrig_H = Cxmrig("H_FARM", ["rig0ED8D9", "rig5E6D1A", "rig12FCF8", "rig12FD7E", "rig40B8E1", "rig40B93E", "rig40B966", "rig39527C"])
    xmrig_B_DOSE1_1 = Cxmrig("B_FARM", ["rig3C086A", "rig3C08D6", "rig40B92F", "rig40B93D", "rigD3ABE7", "rigD3ABF1"])
    xmrig_B_DOSE1_2 = Cxmrig("B_FARM", ["rig1C76F3", "rig1C771C", "rig416783", "rig6F61CF", "rigC49613", "rigC4961B"])
    xmrig_B_DOSE2_1 = Cxmrig("B_FARM", ["rig0040DF", "rig039E17", "rig1D1864", "rig7C4414"])
    xmrig_B_DOSE2_2 = Cxmrig("B_FARM", ["rig3C08AB", "rig3C08BA", "rigC4959E"])
