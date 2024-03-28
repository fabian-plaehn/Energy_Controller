import os
import sys
import time
import requests
import json
from energy_controller.hidden.hidden import *
#from utils import telegram_bot_sendtext


def get_RTC_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"coin_name":"RTC", 
            "miner_name":"xmrig-cc",
            "config":{"pools":[{"algo":"ghostrider", 
                                "url":"stratum-eu.rplant.xyz:7054", 
                                "user":WALLET_RTC[FARM_NAME]+"."+str(rig_id)}],
                      "http": {"enabled": True, "host": "127.0.0.1", "port": 58001},
                      "randomx": {"random1gb-pages": True}
                      }
            }

def get_ZEPH_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"coin_name":"ZEPH",
            "miner_name":"xmrig-cc",
            "config":{"pools":[{"algo":None, 
                                "url":"de.zephyr.herominers.com:1123", 
                                "user":WALLET_ZEPH[FARM_NAME],
                                "pass":str(rig_id)
                                }
                               ],
                      "http": {"enabled": True, "host": "127.0.0.1", "port": 58002},
                      "randomx": {"random1gb-pages": True}
                      }
            }

def get_XDAG_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"coin_name":"XDAG",
            "miner_name":"xmrig-cc",
            "config":{"pools":[{"algo":"rx/xdag", 
                                "url":"stratum.xdag.org:23655", 
                                "user":WALLET_XDAG[FARM_NAME],
                                "pass":str(rig_id)}],
                      "http": {"enabled": True, "host": "127.0.0.1", "port": 58003},
                      "randomx": {"random1gb-pages": True}
                      }
            }
    
def get_YADA_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"coin_name":"YDA",
            "miner_name":"xmrig-cc",
            "config":{"pools":[{"algo":"rx/yada", 
                                "url":"yada.steadnet.net:3333", 
                                "user":WALLET_YADA[FARM_NAME],
                                "pass":str(rig_id)}],
                      "http": {"enabled": True, "host": "127.0.0.1", "port": 58004},
                      "randomx": {"random1gb-pages": True}
                      }
            }
    
def get_QUBIC_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"coin_name":"QUBIC",
            "miner_name":"qli-Client",
            "config":{"Settings":{"amountOfThreads": 22, 
                                                        "baseUrl":"https://mine.qubic.li/",
                                                        #"baseUrl":"https://ai.diyschool.ch/", 
                                                        "allowHwInfoCollect": True,
                                                        "autoupdateEnabled": True,
                                                        "accessToken":WALLET_QUBIC_LI[FARM_NAME],
                                                        "alias":str(rig_id)}
                                            }
            }
    
def get_QUBIC_RQINER_JSON(**kargs):
    FARM_NAME = kargs["farm_name"]
    rig_id = kargs["rig_id"]
    return {"coin_name":"QUBIC",
            "miner_name":"rqiner",
            "config": {"--threads":"32",  "--id": WALLET_QUBIC[FARM_NAME], "--label":str(rig_id)}
            }
    
Flight_Sheets = {
    "RTC":get_RTC_JSON,
    "ZEPH":get_ZEPH_JSON,
    "XDAG":get_XDAG_JSON,
    "YDA":get_YADA_JSON,
    "QUBIC":get_QUBIC_RQINER_JSON
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
                time.sleep(0.1)
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #telegram_bot_sendtext("crashed in CTapo set_sheet")
            #telegram_bot_sendtext(f"{exc_type, fname, exc_tb.tb_lineno}")
            
def run():
    xmrig_H = Cxmrig("B_FARM", ["rig0040DF"])
    xmrig_H.set_sheet("XDAG")
    
if __name__ == "__main__":
    '''xmrig_B = Cxmrig("B_FARM", ['rig0040DF', 'rig039E17', 'rig1C76F3', 'rig1C771C', 'rig1D1864',
                                'rig3C086A',
                                'rig3C08AB',
                                'rig3C08BA',
                                'rig3C08D6',
                                'rig40B92F',
                                'rig40B93D',
                                'rig416783',
                                'rig6F61CF',
                                'rig7C4414',
                                'rigC4959E',
                                'rigC49613', 'rigC4961B',
                                'rigD3ABE7',
                                'rigD3ABF1'])
    xmrig_B.set_sheet("QUBIC")
    
    xmrig_H = Cxmrig("H_FARM", ['rig0ED8D9' , 'rig12FCF8', 'rig12FD7E', 'rig39527C', 'rig40B8E1', 'rig40B93E', 'rig40B966', 'rig5E6D1A'])
    xmrig_H.set_sheet("QUBIC")'''
    
    xmrig_H = Cxmrig("H_FARM", ['DESKTOP-LIJOB68'])
    xmrig_H.set_sheet("ZEPH")
    
    
'''
systemctl stop qli.service
systemctl disable qli.service
systemctl stop mining_cc_daemon
systemctl disable mining_daemon
rm -rf home/user/project

'''
'''
mkdir home/user/project && cd home/user/project && wget http://100.96.102.113:4999/linux/shell_script && chmod +x shell_script && ./shell_script
'''