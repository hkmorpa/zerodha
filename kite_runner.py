import os
import time
import json
import math
import kite_connect
import sys
from operator import itemgetter
from signal import signal, SIGPIPE, SIG_DFL
from zerodha import *

enctoken = os.getenv("enctoken") # set enctoken, REQUIRED field
def myprint(*args):
    debug = "1"
    if(debug == "1"):
        for arg in args:
            print(arg)
                            

def straddle_order(prefix):

    expiry = os.getenv("expiry")
    if expiry == None or expiry == "":
        myprint("please export contract expiry for BANKNIFTY, exiting!")
        return 

    instrument1 = os.getenv("inst1")
    instrument2 = os.getenv("inst2")
    if((instrument1 == None or instrument1 == "") or (instrument2 == None or instrument2 == "")):
        myprint("any of instruments cannot be empty, exiting!")
        return

    order_side = os.getenv("side")

    if(os.getenv("side") == "sell"):
        order_side = client.TRANSACTION_TYPE_SELL
    elif(os.getenv("side") == "buy"):
        order_side = client.TRANSACTION_TYPE_BUY
    else:
        myprint("side can be either buy or sell nothing else, exiting!")
        return


    instrument_prefix = prefix+expiry

    limit_price = 0.0
    order_type = client.ORDER_TYPE_MARKET

    quantity = os.getenv("quantity")
    if quantity == None or quantity == "":
        myprint("quantity is required field")
        return

    size = int(quantity.strip())
    quantity_left = int(size)

    if "BANK" in instrument_prefix:
        single_max_order_size = 900
    else:
        single_max_order_size = 1800

    num_orders = math.ceil(int(size) / single_max_order_size)

    while num_orders > 0:
        order_size = int(min(single_max_order_size, quantity_left))
        num_orders-=1
        quantity_left-=order_size

        total_orders_count, failed_count = place_order_kite(
            instrument=(instrument_prefix+instrument1).upper(),
            side=order_side,
            order_type=order_type,
            price=float(limit_price),
            size=order_size,
        )
        myprint("orders placed for instrument 1: %d, failed: %d" % (total_orders_count, failed_count))
        
        total_orders_count, failed_count = place_order_kite(
            instrument=(instrument_prefix+instrument2).upper(),
            side=order_side,
            order_type=order_type,
            price=float(limit_price),
            size=order_size,
        )
        myprint("orders placed for instrument 2: %d, failed: %d" % (total_orders_count, failed_count))
    myprint("------------------------------------------")
    myprint("\n")

def sell_order(prefix):
    sell_order_type = client.ORDER_TYPE_LIMIT
    expiry = os.getenv("expiry")
    if expiry == None or expiry == "":
        myprint("please export contract expiry for BANKNIFTY, exiting!")
        return 
    sell_instrument = os.getenv("instrument")
    if((sell_instrument == None or sell_instrument == "")):
        myprint("sell instrument cannot be empty, exiting!")
        return

    instrument_prefix = prefix+expiry

    sell_limit_price = 0.0

    sell_price = os.getenv("price")

    if(sell_price == None or sell_price == ""):
        sell_order_type = client.ORDER_TYPE_MARKET
        sell_limit_price = 0
    else:
        sell_limit_price = float(sell_price.strip())
        
    quantity = os.getenv("quantity")
    if quantity == None or quantity == "":
        myprint("quantity is required field")
        return

    size = int(quantity.strip())
    quantity_left = int(size)

    if "BANK" in instrument_prefix:
        single_max_order_size = 900
    else:
        single_max_order_size = 1800

    num_orders = math.ceil(int(size) / single_max_order_size)
    while num_orders > 0:
        order_size = int(min(single_max_order_size, quantity_left))
        num_orders-=1
        quantity_left-=order_size

        total_orders_count, failed_count = place_order_kite(
            instrument=(instrument_prefix+sell_instrument).upper(),
            side=client.TRANSACTION_TYPE_SELL,
            order_type=sell_order_type,
            price=float(sell_limit_price),
            size=order_size,
        )
        myprint("SELL orders placed: %d, failed: %d" % (total_orders_count, failed_count))
    myprint("------------------------------------------")
    myprint("\n")

def buy_order(prefix):
    buy_order_type = client.ORDER_TYPE_LIMIT
    expiry = os.getenv("expiry")
    if expiry == None or expiry == "":
        myprint("please export contract expiry for BANKNIFTY, exiting!")
        return 
    buy_instrument = os.getenv("instrument")

    if(buy_instrument == None or buy_instrument == ""):
        myprint("Buy instrumenti cannot be empty, exiting!")
        return

    instrument_prefix = prefix+expiry

    buy_limit_price = 0.0


    buy_price = os.getenv("price")

    if(buy_price == None or buy_price == ""):
        buy_order_type = client.ORDER_TYPE_MARKET
        buy_limit_price = 0
    else:
        buy_limit_price = float(buy_price.strip())

    quantity = os.getenv("quantity")
    if quantity == None or quantity == "":
        myprint("quantity is required field")
        return

    size = int(quantity.strip())
    quantity_left = int(size)

    if "BANK" in instrument_prefix:
        single_max_order_size = 900
    else:
        single_max_order_size = 1800

    num_orders = math.ceil(int(size) / single_max_order_size)
    while num_orders > 0:
        order_size = int(min(single_max_order_size, quantity_left))
        num_orders-=1
        quantity_left-=order_size

        total_orders_count, failed_count = place_order_kite(
            instrument=(instrument_prefix+buy_instrument).upper(),
            side=client.TRANSACTION_TYPE_BUY,
            size=order_size,
            price=float(buy_limit_price),
            order_type=buy_order_type,
        )
        myprint("BUY orders placed: %d, failed: %d" % (total_orders_count, failed_count))
    myprint("------------------------------------------")
    myprint("\n")

def place_order(prefix):
    buy_order_type, sell_order_type = client.ORDER_TYPE_LIMIT, client.ORDER_TYPE_LIMIT
    expiry = os.getenv("expiry")
    if expiry == None or expiry == "":
        myprint("please export contract expiry for BANKNIFTY, exiting!")
        return 
    buy_instrument = os.getenv("Binstrument")
    sell_instrument = os.getenv("Sinstrument")
    if((buy_instrument == None or buy_instrument == "") and (sell_instrument == None or sell_instrument == "")):
        myprint("Bothinstrumentis cannot be empty, exiting!")
        return

    instrument_prefix = prefix+expiry

    buy_limit_price, sell_limit_price = 0.0, 0.0


    buy_price = os.getenv("Bprice")
    sell_price = os.getenv("Sprice")

    if(buy_price == None or buy_price == ""):
        buy_order_type = client.ORDER_TYPE_MARKET
        buy_limit_price = 0
    else:
        buy_limit_price = float(buy_price.strip())

    if(sell_price == None or sell_price == ""):
        sell_order_type = client.ORDER_TYPE_MARKET
        sell_limit_price = 0
    else:
        sell_limit_price = float(sell_price.strip())
        
    quantity = os.getenv("quantity")
    if quantity == None or quantity == "":
        myprint("quantity is required field")
        return

    size = int(quantity.strip())
    quantity_left = int(size)

    if "BANK" in instrument_prefix:
        single_max_order_size = 900
    else:
        single_max_order_size = 1800

    num_orders = math.ceil(int(size) / single_max_order_size)
    while num_orders > 0:
        order_size = int(min(single_max_order_size, quantity_left))
        num_orders-=1
        quantity_left-=order_size

        if sell_instrument != "" and sell_instrument != None:
            total_orders_count, failed_count = place_order_kite(
                instrument=(instrument_prefix+sell_instrument).upper(),
                side=client.TRANSACTION_TYPE_SELL,
                order_type=sell_order_type,
                price=float(sell_limit_price),
                size=order_size,
            )
            myprint("SELL orders placed: %d, failed: %d" % (total_orders_count, failed_count))
        
        if buy_instrument != "" and buy_instrument != None:
            total_orders_count, failed_count = place_order_kite(
                instrument=(instrument_prefix+buy_instrument).upper(),
                side=client.TRANSACTION_TYPE_BUY,
                size=order_size,
                price=float(buy_limit_price),
                order_type=buy_order_type,
            )
            myprint("BUY orders placed: %d, failed: %d" % (total_orders_count, failed_count))
    myprint("------------------------------------------")
    myprint("\n")

def volatile_strategy(prefix):
    buy_order_type, sell_order_type = client.ORDER_TYPE_LIMIT, client.ORDER_TYPE_LIMIT

    expiry = os.getenv("expiry")
    if expiry == None or expiry == "":
        myprint("please export contract expiry for BANKNIFTY, exiting!")
        return 
    b_instrument = os.getenv("Binstrument")
    s_instrument = os.getenv("Sinstrument")

    buy_instrument = b_instrument;
    sell_instrument = s_instrument;

    b_multiplier = 1
    s_multiplier = 1

    if "*" in b_instrument:
        buy_instrument,multiplier = b_instrument.split("*")
        b_multiplier = int(multiplier)
    if "*" in s_instrument:
        sell_instrument,multiplier = s_instrument.split("*")
        s_multiplier = int(multiplier)

    if((buy_instrument == None or buy_instrument == "") and (sell_instrument == None or sell_instrument == "")):
        myprint("Bothinstrumentis cannot be empty, exiting!")
        return

    instrument_prefix = prefix+expiry

    buy_limit_price, sell_limit_price = 0.0, 0.0


    buy_price = os.getenv("Bprice")
    sell_price = os.getenv("Sprice")

    if(buy_price == None or buy_price == ""):
        buy_order_type = client.ORDER_TYPE_MARKET
        buy_limit_price = 0
    else:
        buy_limit_price = float(buy_price.strip())

    if(sell_price == None or sell_price == ""):
        sell_order_type = client.ORDER_TYPE_MARKET
        sell_limit_price = 0
    else:
        sell_limit_price = float(sell_price.strip())
        
    quantity = os.getenv("quantity")
    if quantity == None or quantity == "":
        myprint("quantity is required field")
        return

    size = int(quantity.strip())
    quantity_left = int(size)

    if "BANK" in instrument_prefix:
        single_max_order_size = 900
    else:
        single_max_order_size = 1800

    num_orders = math.ceil(int(size) / single_max_order_size)
    while num_orders > 0:
        order_size = int(min(single_max_order_size, quantity_left))
        num_orders-=1
        quantity_left-=order_size
        if sell_instrument != "" and sell_instrument != None:
            i = 0
            while i < s_multiplier:
                total_orders_count, failed_count = place_order_kite(
                    instrument=(instrument_prefix+sell_instrument).upper(),
                    side=client.TRANSACTION_TYPE_SELL,
                    order_type=sell_order_type,
                    price=float(sell_limit_price),
                    size=order_size,
                )
                i = i + 1
                myprint("SELL orders placed: %d, failed: %d" % (total_orders_count, failed_count))
        
        if buy_instrument != "" and buy_instrument != None:
            i = 0
            while i < b_multiplier:
                total_orders_count, failed_count = place_order_kite(
                    instrument=(instrument_prefix+buy_instrument).upper(),
                    side=client.TRANSACTION_TYPE_BUY,
                    size=order_size,
                    price=float(buy_limit_price),
                    order_type=buy_order_type,
                )
                i = i + 1
                myprint("BUY orders placed: %d, failed: %d" % (total_orders_count, failed_count))
    myprint("------------------------------------------")
    myprint("\n")


def close_all_positions(positions, side, close_instrument, close_perc):
    open_positions = get_open_positions(positions)
    iteration = 0
    #iteration 0 means we need to close only sell positions 
    #iteration 1 means we need to close only buy positions 
    while iteration < 2:
        for p in open_positions:
            if iteration == 0 and p['open_size'] > 0: #we will close in next iteration
                continue
            if iteration == 1 and p['open_size'] < 0: #we already closed in first iteration
                continue
            if side == "buy" and p['open_size'] < 0:
                continue
            elif side == "sell" and p['open_size'] > 0:
                continue
            elif side == "PE" and "CE" in p['instrument']:
                continue
            elif side == "CE" and "PE" in p['instrument']:
                continue
            elif side == "PEsell" and ("CE" in p['instrument'] or p['open_size'] > 0):
                continue
            elif side == "CEsell" and ("PE" in p['instrument'] or p['open_size'] > 0):
                continue
    
            if close_instrument not in p['instrument']:
                continue
    
            if "NIFTY" not in  p['instrument']:
                print("NIFTY not in %s" % p['instrument'])
                continue

            print("######### Closing position in %s" % p["instrument"])
            print(json.dumps(p, indent=4))
            close_side = client.TRANSACTION_TYPE_SELL if p['open_size'] > 0 else client.TRANSACTION_TYPE_BUY
            order_type = client.ORDER_TYPE_MARKET
            size = 0;

            if p['open_size'] > 0:
                size = (int(p['open_size'] * close_perc / 100)) // 25
                size = size * 25
            else:
                size = -p['open_size']
                size = (int(size * close_perc / 100)) // 25
                size = size * 25

            order_count, failed_count = place_order_kite(
                p['instrument'], side = close_side,
                order_type=order_type,
                price=0.0, size=size)

            myprint("%s orders placed to close position. order count: %d, failed: %d" % (close_side, order_count, failed_count))
        iteration = iteration + 1
        
def cover_orders():

    instruments = os.getenv("instrument")
    perc = os.getenv("perc")
    if not perc:
        perc = 100
    else:
        perc = int(perc)

    if(instruments == None or instruments == ""):
        myprint("instrument cannot be empty, exiting!")
        return

    positions = get_todays_position_info()
    instrument_list = instruments.split(",")

    for instrument in instrument_list:
        close_all_positions(positions, "sell", instrument, close_perc = perc)

    
def stop_loss_runner(sl_amount):
    sl_count = 0
    instruments = os.getenv("instrument")
    instrument_list = []
    if instruments:
        instrument_list = instruments.split(",")
    while True:
        positions = get_todays_position_info()
        i = 0
        net_pnl = 0
        #check if we need to calculate net_pnl for selected instruments only
        while i < len(positions): 
           calculate = 0 
           if instrument_list:
               for inst in instrument_list:
                   if inst in positions[i]["instrument"]:
                       calculate = 1
                       break
           else: 
               calculate = 1
           if calculate == 1: 
                net_pnl += positions[i]["upl"] + positions[i]["rpl"]
           i += 1
        #net_pnl = sum(map(
            #lambda p: p["upl"]+p["rpl"], positions
        #))
        
        myprint("Net PnL: %f" % net_pnl)
        if net_pnl < sl_amount:
            sl_count = sl_count + 1;
            if sl_count > 2:
                myprint("Stop limit reached. stop loss amount: %s, net pnl: %s, closing all positions" % (sl_amount, net_pnl))
                if instruments: #If SL is run for particular instruments then close only those
                    for instrument in instrument_list:
                        close_all_positions(positions, "sell", instrument, close_perc = 100)
                else:
                    close_all_positions(positions, side="sell", close_instrument="", close_perc = 100)
                    close_all_positions(positions, side="buy", close_instrument="", close_perc = 100)
        else:
            sl_count = 0


        print("SL count is %d" % sl_count)

        time.sleep(5)

def main():
    command = os.getenv("command")
    global debug
    debug = os.getenv("debug") # debug 
    if command != None and command != "":
        if command == "close_all":
            side = os.getenv("side")
            perc = os.getenv("perc")
            if perc is None or perc == "":
                perc = 100

            positions = get_todays_position_info()
            if side is None or side == "":
                close_all_positions(positions, side="sell", close_instrument="", close_perc = int(perc))
                close_all_positions(positions, side="buy", close_instrument="", close_perc = int(perc))
            else:
                close_all_positions(positions, side, close_instrument="", close_perc = int(perc))

        elif command == "sell":
            sell_order("BANKNIFTY23")
        elif command == "sell_N":
            sell_order("NIFTY23")
        elif command == "sell_FN":
            sell_order("FINNIFTY23")
        elif command == "buy":
            buy_order("BANKNIFTY23")
        elif command == "buy_N":
            buy_order("NIFTY23")
        elif command == "buy_FN":
            buy_order("FINNIFTY23")
        elif command == "place_order":
            place_order("BANKNIFTY23")
        elif command == "place_N":
            place_order("NIFTY23")
        elif command == "place_FN":
            place_order("FINNIFTY23")
        elif command == "cancel":
            cancel_order()
        elif command == "volatile":
            volatile_strategy("BANKNIFTY23")
        elif command == "volatile_N":
            volatile_strategy("NIFTY23")
        elif command == "volatile_FN":
            volatile_strategy("FINNIFTY23")
        elif command == "straddle":
            straddle_order("BANKNIFTY23")
        elif command == "straddle_N":
            straddle_order("NIFTY23")
        elif command == "straddle_FN":
            straddle_order("FINNIFTY23")
        elif command == "cover":
            cover_orders()
        elif command == "sl_runner":
            sl_amount = os.getenv("sl_amount")
            if sl_amount != None and sl_amount != "":
                sl_amount = float(sl_amount.strip())
                stop_loss_runner(sl_amount)
            else:
                myprint("required sl_amount. Exiting!")
        else:
            myprint("%s command not implemented" % command)
    else:
        myprint("required command. Exiting!")

if __name__ == '__main__':
    client = kite_connect.KiteApp(enctoken=enctoken)
    main()
