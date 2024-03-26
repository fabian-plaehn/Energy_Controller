
class tracking_data:
    def __init__(self, profit, watt) -> None:
        self.profit = profit
        self.watt = watt
        
    def __add__(self, other):
        return tracking_data(self.profit + other.profit, self.watt + other.watt)

    def __repr__(self) -> str:
        return f"proft: {self.profit}, watt: {self.watt}"

def main():
    from collections import deque
    import datetime
    import pandas as pd
    from energy_controller.utils import append_row
    import os
    import sys
    import time
    from typing import List
    from energy_controller.utils import Main_Restart_Exception, logger, maximize_with_constraint, minimize_with_constraint, telegram_bot_sendtext
    from numpy import mean
    from energy_controller.sunny.CSunny import EnergyController
    telegram_bot_sendtext(f"import mining stacks")
    from energy_controller.tapo.CTapo import Mining_Stacks, MiningStack
    from energy_controller.coins.Coins import coins
    telegram_bot_sendtext(f"imports done")
    
    # init classes
    telegram_bot_sendtext(f"init Energy class")
    CEnergyController = EnergyController()
    
    check_every = 120
    last_check = time.time()-120
    try:
        while True:
            usable_power = CEnergyController.get_usable_power()
            
            time.sleep(1)
            if (time.time() - last_check) < check_every:
                continue
            
            last_check = time.time()
            
            for coin in coins:
                coin.get_profitability()
                print(coin.name, coin.revenue, coin.profitability, coin.break_even_watt, coin.price, coin.network_hashrate, coin.difficulty)
                telegram_bot_sendtext(f"{coin.name, coin.profitability, coin.break_even_watt}")

            for stack in Mining_Stacks:
                stack.update_coin([coin for coin in coins if coin.minable])

            logger("Usable Power: " + str(usable_power), "info")
            telegram_bot_sendtext("Usable Power: " + str(usable_power))
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

                        telegram_bot_sendtext(f"turn on profit sheet for stack: {stack.name}, sheet difference: {stack.efficient_watt_difference}")
                        telegram_bot_sendtext("Usable Power now: " + str(usable_power))
                        logger(f"turn on profit sheet for stack: {stack.name}", "info")
                        stack.efficient_sheet = False

                if usable_power > 0:    
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
                    telegram_bot_sendtext(f"turn on efficient sheet for stack: {stack.name}, sheet difference: {stack.efficient_watt_difference}")
                    telegram_bot_sendtext("Usable Power now: " + str(usable_power))
                    stack.efficient_sheet = True

                if usable_power < 0:
                    stacks_to_turn_off: List[MiningStack] = [x[0] for x in minimize_with_constraint(relevant_stacks, abs(usable_power))]
                    
                    if len(stacks_to_turn_off) == 0:  # minimize return list of rigs with consumption higher than defizit
                        # if its not possible bcs the defizit is too high list is empty -> then turn off everything
                        stacks_to_turn_off = [stack for stack in Mining_Stacks if (stack.get_status() and not stack.always_on_stacks)]  # has to be on to be turned off

                    for stack in stacks_to_turn_off:
                        telegram_bot_sendtext(f"Turn off: {stack.name}")
                        stack.turn_off()
                
            dataset = {}
            for stack in Mining_Stacks:
                if stack.get_status():
                    if stack.CHive.farm_name not in dataset:
                        dataset[stack.CHive.farm_name] = {}
                    if stack.current_coin not in dataset[stack.CHive.farm_name]:
                        dataset[stack.CHive.farm_name][stack.current_coin] = tracking_data(0, 0)
                    dataset[stack.CHive.farm_name][stack.current_coin] += tracking_data(stack.current_revenue, stack.current_watt)

            print(dataset)
            for key, value in dataset.items():
                #  key # farm name
                #  value # dict{Coin:tracking_data}
                sum_track = tracking_data(0, 0)
                for key_c, value_c in value.items():
                    sum_track += value_c
                    try:
                        df = pd.read_csv(f"dataset/{key}/{key_c}.txt")
                    except FileNotFoundError:
                        try:
                            os.mkdir(f"dataset/{key}")
                        except Exception:
                            pass
                        with open(f"dataset/{key}/{key_c}.txt", "w") as f:
                            f.write(f"Time,kWh,Product_Day")
                        df = pd.read_csv(f"dataset/{key}/{key_c}.txt")
                            
                    date_now = datetime.datetime.now().strftime("%d/%m/%Y")
                    if date_now not in list(df["Time"]):
                        new_row = pd.Series({"Time":date_now,"kWh":value_c.watt/1000*(time.time()-stack.set_sheet_time)/(60*60),
                                             "Product_Day":value_c.profit*(time.time()-stack.set_sheet_time)/(24*60*60)})
                        df = append_row(df, new_row)
                    else:
                        df[f"kWh"][(df["Time"] == date_now)] += value_c.watt/1000*(time.time()-stack.set_sheet_time)/(60*60)
                        df[f"Product_Day"][(df["Time"] == date_now)] += value_c.profit*(time.time()-stack.set_sheet_time)/(24*60*60)
                    df.to_csv(f"dataset/{key}/{key_c}.txt", sep=",", index=False)
                try:
                    df = pd.read_csv(f"dataset/{key}/summation.txt")
                except FileNotFoundError:
                    try:
                        os.mkdir(f"dataset/{key}")
                    except Exception:
                        pass
                    with open(f"dataset/{key}/summation.txt", "w") as f:
                        f.write(f"Time,kWh,Product_Day")
                    df = pd.read_csv(f"dataset/{key}/summation.txt")
                        
                date_now = datetime.datetime.now().strftime("%d/%m/%Y")
                if date_now not in list(df["Time"]):
                    new_row = pd.Series({"Time":date_now,"kWh":sum_track.watt/1000*(time.time()-stack.set_sheet_time)/(60*60),
                                        "Product_Day":sum_track.profit*(time.time()-stack.set_sheet_time)/(24*60*60)})
                    df = append_row(df, new_row)
                else:
                    df[f"kWh"][(df["Time"] == date_now)] += sum_track.watt/1000*(time.time()-stack.set_sheet_time)/(60*60)
                    df[f"Product_Day"][(df["Time"] == date_now)] += sum_track.profit*(time.time()-stack.set_sheet_time)/(24*60*60)
                df.to_csv(f"dataset/{key}/summation.txt", sep=",", index=False)
                    
            for stack in Mining_Stacks:
                stack.set_sheet()
                
            # dataset
    except Main_Restart_Exception:
        telegram_bot_sendtext("Main_Restart_Exception raised")
        return 0
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        telegram_bot_sendtext("crashed")
        telegram_bot_sendtext(f"{exc_type, fname, exc_tb.tb_lineno}")  


if __name__ == "__main__":
    main()
