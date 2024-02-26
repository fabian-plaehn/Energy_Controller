import datetime
import math
from time import ctime, time, sleep
from typing import List, Tuple
from itertools import permutations
import numpy as np
import requests
from hidden.hidden import bot_chatID, bot_token
_debug = False
_info = True
_trace = False


def telegram_bot_sendtext(bot_message):
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

    return list(max_elements)


def minimize_with_constraint(tlist: List[Tuple[object, float, float]], constraint_first_number: float) -> List[Tuple[object, float, float]]:
    min_sum = math.inf
    min_elements = []
    for i in range(len(tlist)):
        for j in permutations(tlist, i + 1):
            if constraint_first_number <= sum([x[1] for x in j]): # if rigs needs more than contraint -> viable
                if sum(x[2] for x in j) < min_sum:
                    min_elements = j

    return list(min_elements)


if __name__ == '__main__':
    print(maximize_with_constraint([(np.random.randint(low=0, high=10), np.random.randint(low=0, high=10)) for i in range(5)], 10))