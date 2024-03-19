import os
import sys
import time
import requests
import json
from energy_controller.hidden.hidden import WALLET_RTC, WALLET_ZEPH, WALLET_XDAG, WALLET_YADA, xmrig_server_ip, WALLET_QUBIC
#from utils import telegram_bot_sendtext


def get_RTC_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"miner_name":"RTC", "config":{"pools":[{"algo":"ghostrider", 
                                                             "url":"stratum-eu.rplant.xyz:7054", 
                                                             "user":WALLET_RTC[FARM_NAME]}]}+"."+str(rig_id)}

def get_ZEPH_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"miner_name":"ZEPH", "config":{"pools":[{"algo":None, 
                                                            "url":"de.zephyr.herominers.com:1123", 
                                                            "user":WALLET_ZEPH[FARM_NAME],
                                                            "pass":str(rig_id)}]}}

def get_XDAG_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"miner_name":"XDAG", "config":{"pools":[{"algo":"rx/xdag", 
                                                            "url":"stratum.xdag.org:23655", 
                                                            "user":WALLET_XDAG[FARM_NAME],
                                                            "pass":str(rig_id)}]}}
    
def get_YADA_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"miner_name":"YDA", "config":{"pools":[{"algo":"rx/yada", 
                                                            "url":"yada.steadnet.net:3333", 
                                                            "user":WALLET_YADA[FARM_NAME],
                                                            "pass":str(rig_id)}]}}
    
def get_QUBIC_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"miner_name":"QUBIC", "config":{"Settings":{"amountOfThreads": 16, 
                                                        "baseUrl":"https://ai.diyschool.ch/", 
                                                        "accessToken":WALLET_QUBIC[FARM_NAME],
                                                        "alias":str(rig_id)}}}
    
Flight_Sheets = {
    "RTC":get_RTC_JSON,
    "ZEPH":get_ZEPH_JSON,
    "XDAG":get_XDAG_JSON,
    "YDA":get_YADA_JSON,
    "QUBIC":get_QUBIC_JSON
}

class Cxmrig:
    def __init__(self, farm_name, worker_ids) -> None:
        self.farm_name = farm_name
        self.worker_ids = worker_ids
        
    def set_sheet(self, name):
        try:
            for worker_id in self.worker_ids:
                get_sheet = Flight_Sheets[name](farm_name=self.farm_name, rig_id=worker_id)
                requests.get(f"http://100.96.102.113:4999/set_miner/{worker_id}", json=get_sheet)
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #telegram_bot_sendtext("crashed in CTapo set_sheet")
            #telegram_bot_sendtext(f"{exc_type, fname, exc_tb.tb_lineno}")
            
def run():
    xmrig_H = Cxmrig("B_FARM", ["rig0040DF"])
    xmrig_H.set_sheet("XDAG")
    
if __name__ == "__main__":
    xmrig_B = Cxmrig("B_FARM", ['rig0040DF', 'rig039E17', 'rig1C76F3', 'rig1C771C', 'rig416783', 'rig6F61CF', 'rigC49613', 'rigC4961B', 'rig40B92F', 'rig416783'])
    xmrig_B.set_sheet("QUBIC")
    
    xmrig_H = Cxmrig("H_FARM", ['rig0ED8D9' , 'rig12FCF8', 'rig39527C'])
    xmrig_H.set_sheet("QUBIC")