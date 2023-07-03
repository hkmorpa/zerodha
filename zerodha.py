import os
import time
import json
import math
import kite_connect
import sys
from operator import itemgetter
from signal import signal, SIGPIPE, SIG_DFL

enctoken = os.getenv("enctoken")
client = kite_connect.KiteApp(enctoken=enctoken)

def get_client_order_id():
    return "IRIS-{timestamp}".format(timestamp=round(time.time() * 1000))

def cancel_order():
    orders = client.orders()
    order_ids = [order['order_id'] for order in orders if order['status'] == 'OPEN']
    for order_id in order_ids:
        client.cancel_order(
            variety=client.VARIETY_REGULAR,
            order_id=order_id)

def pnl(entry_price, exit_price, size, side):
    if side == "buy":
        return (exit_price-entry_price)*size
    return (entry_price - exit_price)*size

def prepare_position_info(position_data, last_price):
    position = {
        "instrument": position_data["tradingsymbol"],
        "entry_price": position_data["buy_price"] if position_data['buy_quantity'] > position_data['sell_quantity'] else position_data["sell_price"],
        "exit_price": position_data["sell_price"] if position_data['buy_quantity'] > position_data['sell_quantity'] else position_data["buy_price"],
        "side": "buy" if position_data['buy_quantity'] > position_data['sell_quantity'] else "sell",
        "rpl": 0,
        "upl": 0,
        "open_size": position_data["quantity"],
        "last_price": last_price
    }
    if position_data["sell_quantity"] > 0 and position_data["buy_quantity"] > 0:
        position["rpl"] =  pnl(
            float(position_data['buy_price']), 
            float(position_data['sell_price']), 
            abs(min(float(position_data['buy_quantity']), float(position_data['sell_quantity']))), 
            "buy"
        ) 
    position["upl"] = pnl(
        position['entry_price'], 
        last_price, abs(position_data['quantity']), 
        side=position["side"])
    return position
    

def get_open_positions(positions):
    return list(filter(
        lambda p: p["open_size"] != 0, positions
    ))

def get_todays_position_info():
    positions_data = client.positions()
    #print(positions_data)
    positions = []
    
    ltp_data = client.ltp(list(map(lambda i: "NFO:"+i['tradingsymbol'], positions_data["net"])))
    for p in positions_data["net"]:
        #We need to consider only NIFTY contracts
        if "NIFTY" not in p["tradingsymbol"]:
            continue
        trading_symbol = "NFO:"+p["tradingsymbol"]
        if  trading_symbol not in ltp_data and p["quantity"] != 0:
            print("failed to get ltp for %s, will fail to calculate unrealised pnl" % p["tradingsymbol"])
            continue
        positions.append(prepare_position_info(p, ltp_data[trading_symbol]["last_price"])) 
    return positions

def place_order_kite(instrument, side, order_type, price, size):


    if "BANK" in instrument:
        single_max_order_size = 900
    else:
        single_max_order_size = 1800
    num_orders = math.ceil(int(size) / single_max_order_size)
    quantity_left = int(size)
    orders = []
    failed_count = 0
    print("%s %s, %s %s, %s"% (instrument, side, order_type, price, size))
    while num_orders > 0:
        order_size = int(min(single_max_order_size, quantity_left))
        num_orders-=1
        quantity_left-=order_size
        order_response = client.place_order(
            variety=client.VARIETY_REGULAR,
            product=client.PRODUCT_NRML,
            exchange=client.EXCHANGE_NFO,
            validity=client.VALIDITY_DAY,
            tradingsymbol=instrument,
            transaction_type=side,
            quantity=order_size,
            price=price,
            order_type=order_type,
            disclosed_quantity=0,
            trigger_price=0,
            squareoff=0,
            stoploss=0,
            trailing_stoploss=0,
            tag=get_client_order_id()
        )
        
        if order_response["data"] and order_response["data"]["order_id"]:
            orders.append(order_response["data"])
            print("%s order placed on instrument %s order_id %s, price: %s, size: %s, order_type: %s" % (side, instrument, order_response["data"]["order_id"], price, order_size, order_type))
        else:
            failed_count += 1
            print("failed to place order")
    return num_orders, failed_count
