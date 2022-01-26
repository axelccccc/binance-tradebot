import json, websocket, threading

from . import stream as st
from .gui import bot_display

class WebSocketClient():

    def __init__(self, owner):

        self.main_bot = owner

        self.make_binance_socket(self.main_bot.streams, self.main_bot.testnet)

        self.ws = websocket.WebSocketApp(
            self.socket, 
            on_open=on_open, 
            on_close=on_close, 
            on_message=on_message, 
            on_error=on_error)

        



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

def on_close(ws):
    print('closed connection')

def on_error(ws, error):
    print(error)


def on_message(ws, message):
    from .stream import _sga
    
    json_message = json.loads(message)

    _sga.process(json_message)

    bot_display()