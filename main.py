from collections import deque
import os
import sys
import time
from typing import List
from utils import logger, maximize_with_constraint, minimize_with_constraint, telegram_bot_sendtext

from numpy import mean
from sunny.CSunny import EnergyController

telegram_bot_sendtext(f"import mining stacks")
from tapo.CTapo import Mining_Stacks, MiningStack

from coins.Coins import coins

telegram_bot_sendtext(f"imports done")
def main():
    # init classes
    telegram_bot_sendtext(f"init Energy class")
    CEnergyController = EnergyController()
    
    check_every = 120
    last_check = time.time()-120
    q_pvpower = deque(maxlen=20)
    q_csmp = deque(maxlen=20)
    
    no_data_counter = 0
    no_data_max_count = 20
    try:
        while True:
            CEnergyData = CEnergyController.get_data()
            if CEnergyData is None:
                logger("No data available", "info")
                telegram_bot_sendtext("No data available")
                no_data_counter += 1
                time.sleep(2)
                
                if no_data_counter >= no_data_max_count:
                    CEnergyController.reset()
                    no_data_counter = 0
                continue

            q_pvpower.append(CEnergyData.pvpower)
            q_csmp.append(CEnergyData.csmp)
            
            pvpower = mean(list(q_pvpower))
            csmp = mean(list(q_csmp))
            
            time.sleep(1)
            
            if (time.time() - last_check) < check_every:
                continue
            
            last_check = time.time()
            logger(f"{CEnergyData}", "info")
            logger(f"mean_pv_power: {pvpower}, mean_csmp: {csmp}", "info")
            telegram_bot_sendtext(f"mean_pv_power: {pvpower}, mean_csmp: {csmp}, battery_status: {CEnergyData.batterystatus}, battery_power: {CEnergyData.batterypower}")

            if pvpower > csmp:
                usable_power = pvpower - csmp
            elif CEnergyData.batterystatus > 20:  # draw until x percent battery
                usable_power = 0  # dont add or shutdown rigs
                if CEnergyData.batterypower > CEnergyData.max_battery_power:  # dont exceed battery power limit else you will pull from grid
                    usable_power = CEnergyData.max_battery_power - CEnergyData.batterypower  # go down by difference
                elif CEnergyData.batterystatus > 60:  # greater than 60 not exceeding the powerlimit boot up some rigs
                    usable_power = max(CEnergyData.max_battery_power - CEnergyData.batterypower-500, 0)
                    
            else:
                usable_power = pvpower - csmp  # negative


            for coin in coins:
                coin.get_profitability()
                print(coin.name, coin.revenue, coin.profitability, coin.break_even_watt, coin.price, coin.network_hashrate, coin.difficulty)

            for stack in Mining_Stacks:
                stack.update_coin()

            logger("Usable Power: " + str(usable_power), "info")

            if usable_power >= 0:  # turn on rigs
                relevant_stacks = [(stack, stack.watt_efficient, stack.even_watt_rate) for stack in Mining_Stacks if (not stack.get_status() and not stack.always_on_stacks)]  # has to be off to be turned on
                if len(relevant_stacks) == 0:  # maybe even turn on profit over efficiency
                    for stack in Mining_Stacks:
                        if not stack.efficient_sheet:
                            continue

                        if usable_power < stack.efficient_watt_difference:
                            continue

                        usable_power -= stack.efficient_watt_difference
                        #  enough power and profit sheet not activated yet

                        logger(f"turn on profit sheet for stack: {stack.name}", "info")
                        telegram_bot_sendtext(f"turn on profit sheet for stack: {stack.name}")
                        stack.efficient_sheet = False

                if usable_power <= 0:
                    continue
                stacks_to_turn_on: List[MiningStack] = [x[0] for x in maximize_with_constraint(relevant_stacks, abs(usable_power))]

                for stack in stacks_to_turn_on:
                    telegram_bot_sendtext(f"Turn on: {stack.name}")
                    stack.turn_on()
            else:  # turn off rigs
                # switch from profit to efficiency
                relevant_stacks = [(stack, stack.watt_efficient, stack.even_watt_rate) for stack in Mining_Stacks if (stack.get_status() and not stack.always_on_stacks)]  # has to be on to be turned off

                for stack, _, _ in relevant_stacks:
                    if stack.efficient_sheet:
                        continue

                    if usable_power >= 0:
                        continue
                    #  defizit power and efficient sheet not activated yet
                    usable_power += stack.efficient_watt_difference
                    logger(f"turn on efficient sheet for stack: {stack.name}", "info")
                    telegram_bot_sendtext(f"turn on efficient sheet for stack: {stack.name}")
                    stack.efficient_sheet = True

                if usable_power >= 0:
                    continue
                stacks_to_turn_off: List[MiningStack] = [x[0] for x in minimize_with_constraint(relevant_stacks, abs(usable_power))]
                
                if len(stacks_to_turn_off) == 0:  # minimize return list of rigs with consumption higher than defizit
                    # if its not possible bcs the defizit is too high list is empty -> then turn off everything
                    stacks_to_turn_off = [stack for stack in Mining_Stacks if (stack.get_status() and not stack.always_on_stacks)]  # has to be on to be turned off

                for stack in stacks_to_turn_off:
                    telegram_bot_sendtext(f"Turn off: {stack.name}")
                    stack.turn_off()
                
            for stack in Mining_Stacks:
                stack.set_sheet()
                
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        telegram_bot_sendtext("crashed")
        telegram_bot_sendtext(f"{exc_type, fname, exc_tb.tb_lineno}")  


if __name__ == "__main__":
    main()
