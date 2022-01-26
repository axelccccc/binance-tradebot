import json, os
from typing import Dict

# ENUMS

INTERVAL_VALUES = (
    '1m','3m','5m','15m',
    '30m','1h','2h','4h',
    '6h','8h','12h','1d',
    '3d','1w','1M'
    )



# PATHS

CONFIG_PATH = 'private/config.json'
DATA_PATH = 'data/'
USER_DATA = 'user_data.json'
ORDERS_DATA = 'orders.json'

def user_data_path() -> str:
    cfg = load_data(CONFIG_PATH)
    if cfg['testnet']:
        return DATA_PATH + 'test_' + USER_DATA
    else:
        return DATA_PATH + USER_DATA
        
def orders_data_path() -> str:
    cfg = load_data(CONFIG_PATH)
    if cfg['testnet']:
        return DATA_PATH + 'test_' + ORDERS_DATA
    else:
        return DATA_PATH + ORDERS_DATA


# BASE (!!! FOR JSON DATA)

def save_data(data, filepath, mode):
    path = os.path.dirname(filepath)

    if not os.path.isdir(path):
        os.makedirs(path)

    with open(filepath, mode) as f:
        json.dump(data, f, indent=4)

def load_data(filepath):
    path = os.path.dirname(filepath)
    file = os.path.basename(filepath)

    try:
        if not os.path.isdir(path):
            os.makedirs(path)
        with open(filepath) as f:
            if os.path.getsize(filepath):
                data = json.load(f)
                return data
            else:
                return []
    except FileNotFoundError:
        with open(filepath, 'w') as f:
            return []



# ORDERS

def load_orders(symbol):
    data_json = load_data(orders_data_path())
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
        'usd': round(float(order['cummulativeQuoteQty']), 2),
        'close_value': close_value
    }
    return formatted_order



# CONFIG

def load_config():

    config = load_data(CONFIG_PATH)

    if not config:

        config = {

            'telegram_bot_token': '',
            'telegram_user_id': 0,
            'binance_api_key': '',
            'binance_api_key_testnet': '',
            'binance_api_secret': '',
            'binance_api_secret_testnet': '',

            'testnet': False,
            'dollar': 'USDT',
            'markets': [],
            'intervals': [],
            'start_qties': [],
            'strategies': [],
            'sizers': []

        }

        save_data(config, CONFIG_PATH, 'w')

    return config