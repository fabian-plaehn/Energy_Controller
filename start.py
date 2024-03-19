from multiprocessing import Process
import time
from energy_controller.utils import telegram_bot_sendtext, kill_ff
from main import main


def start():
    while True:
        p = Process(target=main)
        p.start()
        p.join()
        telegram_bot_sendtext("clean up")
        time.sleep(5)
        # clean up
        for _ in range(5):
            while True:
                try:
                    kill_ff()
                    break
                except:
                    break
            time.sleep(1)
        telegram_bot_sendtext("restart main")



if __name__ == "__main__":
    start()