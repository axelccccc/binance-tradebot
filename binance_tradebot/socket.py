import json, websocket, threading
import datetime as dt

from . import stream as st
from .gui import bot_display

_wga = None
""" WebSocketClient global access variable\n
    Used for on_close() to access the bot's websocket \n
    and relaunch it if necessary
    """


class WebSocketClient():

    def __init__(self, owner):

        # global _wga

        self.main_bot = owner

        self.make_binance_socket(self.main_bot.streams, self.main_bot.testnet)

        self.ws = websocket.WebSocketApp(
            self.socket, 
            on_open=on_open, 
            on_close=on_close, 
            on_message=on_message, 
            on_error=on_error)

        # _wga = self

        



    def make_binance_socket(self, streams: st.Streams, testnet=False):

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

        self.socket = socket

    
    def run(self):
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.start()

    def stop(self):
        self.ws.close()
        self.ws_thread.join()



def on_open(ws):
    print('opened connection')

def on_close(ws, status_code, message):
    from binance_tradebot.telegram import _tga
    # global _wga
    print(f'closed connection with code: {status_code} — {message}')
    time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
    _tga.telebot.send_message(_tga.main_bot.config['telegram_user_id'], (
        "Streams stopped at %s with code : %d — %s" % time, status_code, message))
    # _wga.main_bot.restart_streams()

def on_error(ws, error):
    from binance_tradebot.telegram import _tga
    time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
    _tga.telebot.send_message(_tga.main_bot.config['telegram_user_id'], (
        "Error occured on streams at %s : %s" % time, error))
    print(error)


def on_message(ws, message):
    from .stream import _sga
    
    json_message = json.loads(message)

    _sga.process(json_message)

    bot_display()