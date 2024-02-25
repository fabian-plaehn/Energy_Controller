import time
from typing import List

from sunny.CSunny import EnergyController
from tapo.CTapo import Mining_Stacks, MiningStack
from utils import logger, maximize_with_constraint, minimize_with_constraint
from coins.Coins import coins

def main():
    # init classes
    
    
    CEnergyController = EnergyController()

    while True:
        CEnergyData = CEnergyController.get_data()
        if CEnergyData is None:
            logger("No data available", "info")
            continue


        if CEnergyData.pvpower > CEnergyData.csmp:
            usable_power = CEnergyData.pvpower - CEnergyData.csmp
        elif CEnergyData.batterystatus > 20:  # draw until x percent battery
            usable_power = 0  # dont add or shutdown rigs
        else:
            usable_power = CEnergyData.pvpower - CEnergyData.csmp  # negative


        for coin in coins:
            coin.get_profitability()
            print(coin.name, coin.revenue, coin.profitability, coin.break_even_watt, coin.price, coin.network_hashrate, coin.difficulty)

        for stack in Mining_Stacks:
            stack.update_coin()

        logger("Usable Power: " + str(usable_power), "info")

        if usable_power >= 0:  # turn on rigs
            relevant_stacks = [(stack, stack.watt, stack.profit) for stack in Mining_Stacks if (not stack.get_status() and not stack.always_on_stacks)]  # has to be off to be turned on
            if len(relevant_stacks) == 0:  # maybe even turn on profit over efficiency
                for stack in Mining_Stacks:
                    if not stack.efficient_sheet:
                        continue

                    if usable_power < stack.efficient_watt_difference:
                        continue

                    usable_power -= stack.efficient_watt_difference
                    #  enough power and profit sheet not activated yet

                    logger(f"turn on profit sheet for stack: {stack.name}", "info")
                    stack.efficient_sheet = False

            stacks_to_turn_on: List[MiningStack] = [x[0] for x in maximize_with_constraint(relevant_stacks, abs(usable_power))]
            for stack in stacks_to_turn_on:
                stack.turn_on()
        else:  # turn off rigs
            # switch from profit to efficiency
            for stack in Mining_Stacks:
                if stack.efficient_sheet:
                    continue

                if usable_power > 0:
                    continue
                #  enough power and profit sheet not activated yet
                usable_power += stack.efficient_watt_difference
                logger(f"turn on efficient sheet for stack: {stack.name}", "info")
                stack.efficient_sheet = True

            relevant_stacks = [(stack, stack.watt_efficient, stack.watt_even) for stack in Mining_Stacks if (stack.get_status() and not stack.always_on_stacks)]  # has to be on to be turned off
            stacks_to_turn_off: List[MiningStack] = [x[0] for x in minimize_with_constraint(relevant_stacks, abs(usable_power))]
            for stack in stacks_to_turn_off:
                stack.turn_off()

        for stack in Mining_Stacks:
            stack.set_sheet()

        time.sleep(120)


if __name__ == "__main__":
    main()
