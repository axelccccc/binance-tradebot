import json, websocket
from os import system
from pprint import pprint

from binance_tradebot.exceptions import MissingClientOrStreams

from . import stream as st
from . import config as cfg
from . import exceptions as exc
from .gui import bot_display

ws = None

def make_binance_socket(streams: st.Streams, testnet=False) -> str:

    if testnet:
        socket_base = "wss://testnet.binance.vision/"
    else:
        socket_base = "wss://stream.binance.com:9443/"

    if streams:
        if len(streams) == 1:
            socket = socket_base + 'ws/' + streams[0].name
        else:
            socket = socket_base + 'stream?streams=' + \
                ''.join(streams[i].name + '/' for i in range(0, len(streams)-1)) + \
                    streams[-1].name
    else:
        raise Exception

    return socket



def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_error(ws, error):
    print(error)


def on_message(ws, message):
    from .stream import _streams_global_access as _sga
    
    json_message = json.loads(message)

    _sga.process(json_message)

    bot_display()

    """ for stream in _sga:
        print(stream)
        print(stream.close_values)
        pprint(stream.strategy.info()) """



def run(streams):
    global ws


    if cfg.bot_is_configured:
        link = make_binance_socket(streams, testnet=cfg.TESTNET)
    else:
        raise exc.BotNotConfigured

    from .api import client
    from .stream import _streams_global_access as _sga

    if not (client and _sga):
        raise MissingClientOrStreams

    ws = websocket.WebSocketApp(link, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
    ws.run_forever()