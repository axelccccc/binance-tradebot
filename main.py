#########################################
# BINANCE TRADING BOT
#
# For SPOT Trading & Market Orders
# Supports multiple simulatenous streams
#
#########################################

import fire

from binance.enums import *

from binance_tradebot import config as cfg
from binance_tradebot import stream as st
from binance_tradebot import socket



# Main

def main():

    fire.Fire(cfg.set_config)

    s = st.Streams()
    socket.run(s)

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)