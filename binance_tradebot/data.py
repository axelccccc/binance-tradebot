import json, os
from typing import Dict

from . import config as cfg

def save_data(data, file, mode):
    if not os.path.isdir(cfg.DATA_PATH):
        os.makedirs(cfg.DATA_PATH)

    with open(file, mode) as f:
        json.dump(data, f)

def load_data(file):
    try:
        if not os.path.isdir(cfg.DATA_PATH):
            os.makedirs(cfg.DATA_PATH)
        with open(file) as f:
            if os.path.getsize(cfg.ORDERS_DATA_PATH):
                data = json.load(f)
                return data
            else:
                return []
    except FileNotFoundError or json.JSONDecodeError:
        with open(file, 'r') as f:
            return []

def load_orders(symbol):
    data_json = load_data(cfg.ORDERS_DATA_PATH)
    data = []
    if data_json != None:
        for order in data_json:
            if order['symbol'] == symbol:
                data.append(order)
    return data

def format_order(order, close_value) -> Dict:
    """Format Binance order data for program usage & storage in database"""
    formatted_order = {
        'symbol': order['symbol'],
        'time': order['transactTime'],
        'side': order['side'],
        'qty': float(order['executedQty']),
        'price': float(order['price']),
        'usd': float('%.2f' % order['cummulativeQuoteQty']),
        'close_value': close_value
    }
    return formatted_order