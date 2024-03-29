import datetime
import itertools
import math
import string
from time import ctime, time, sleep
from typing import List, Tuple
from itertools import permutations
import pandas as pd
import psutil
import numpy as np
import requests
from energy_controller.hidden.hidden import bot_token, bot_chatID
_debug = False
_info = True
_trace = False


class Main_Restart_Exception(Exception):
    pass


def kill_ff():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == "firefox.exe" or proc.name() == "geckodriver.exe":
            proc.kill()
            
            
def append_row(df, row):
    return pd.concat([
                df, 
                pd.DataFrame([row], columns=row.index)]
           ).reset_index(drop=True)
            

def telegram_bot_sendtext(bot_message : str):
    bot_message = bot_message.replace("_", "")
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


def logger(info, level='debug'):
    """
    Log output to the console (if verbose output is enabled)

    """
    import logging
    if not globals()[f'_{level}']:
        return

    logging.basicConfig(level=getattr(logging, level.swapcase()),
                        handlers=[logging.StreamHandler()])
    logger = logging.getLogger(__name__)
    currentDateAndTime = datetime.datetime.now()
    getattr(logger, level if hasattr(logger, level) else 'debug')(
        f"{currentDateAndTime.strftime('%H:%M:%S')}| " + str(info))


def maximize_with_constraint(tlist: List[Tuple[object, float, float]], constraint_first_number: float) -> List[Tuple[object, float, float]]:
    # List[Object, constraint, maximize]
    max_sum = -math.inf
    max_elements = []
    for i in range(len(tlist)):
        for j in permutations(tlist, i + 1):
            if constraint_first_number >= sum([x[1] for x in j]):  # if rigs need less than contraint -> viable
                if sum(x[2] for x in j) > max_sum:
                    max_elements = j
                    max_sum = sum(x[2] for x in j)

    return list(max_elements)


def minimize_with_constraint(tlist: List[Tuple[object, float, float]], constraint_first_number: float) -> List[Tuple[object, float, float]]:
    min_sum = math.inf
    min_elements = []
    for i in range(len(tlist)):
        for j in permutations(tlist, i + 1):
            if constraint_first_number <= sum([x[1] for x in j]): # if rigs needs more than contraint -> viable
                if sum(x[2] for x in j) < min_sum:
                    min_elements = j
                    min_sum = sum(x[2] for x in j)

    return list(min_elements)
        
def king_of_max(object_list):
    for i in range(len(object_list)):
        print(list(itertools.combinations(object_list, i+1)))
        for elements in list(itertools.combinations(object_list, i+1)):
            print(list(itertools.product(*elements))) 
    
    pass

if __name__ == '__main__':
    object_list = [[[i, np.random.randint(low=0, high=10), np.random.randint(low=0, high=10)] for j in range(2)] for i in range(4)]
    king_of_max(object_list)
    '''object_list = [(1, np.random.randint(low=0, high=10), np.random.randint(low=0, high=10)) for i in range(5)]
    print(object_list)
    print(minimize_with_constraint(object_list, 10))'''