import telebot as tb, threading
import datetime as dt

from . import data
from . import exceptions as exc
from .utils import are_subclass_of

# This version implements the barebones telegram bot behavior,
# while the full interface version is being developed

# ThreadedTelegramHandler Global Access
_tga = None

class ThreadedTelegramHandler():

    def __init__(self, owner, bot_token: str):

        global _tga

        self.main_bot = owner

        self.main_bot.save_state()

        ##### TELEGRAM BOT OBJECTS & CLASSES #####

        class UserFilter(tb.SimpleCustomFilter):
            key='is_correct_user'
            @staticmethod
            def check(message: tb.types.Message):
                return message.from_user.id == self.main_bot.config['telegram_user_id']

        self.telebot = tb.TeleBot(bot_token)

        self.telebot.add_custom_filter(UserFilter())

        _tga = self

        

        self.telebot.send_message(self.main_bot.config['telegram_user_id'], "Bot successfully started")



        ##### MESSAGE HANDLERS #####

        @self.telebot.message_handler(
            func=lambda message: True,
            is_correct_user=True
        )

        def main_msg_handling(message: tb.types.Message):

            # Exit

            if message.text == 'exit':
                self.main_bot.stop()

            # Setup messages

            if message.text.startswith('api key ') and not message.text.startswith('api key testnet '):
                self.main_bot.config['binance_api_key'] = message.text[8:]
                self.main_bot.save_state()
                self.telebot.reply_to(message, 'API Key set')

            if message.text.startswith('api secret ') and not message.text.startswith('api secret testnet '):
                self.main_bot.config['binance_api_secret'] = message.text[11:]
                self.main_bot.save_state()
                self.telebot.reply_to(message, 'API Secret set')

            if message.text.startswith('api key testnet '):
                self.main_bot.config['binance_api_key_testnet'] = message.text[16:]
                self.main_bot.save_state()
                self.telebot.reply_to(message, 'Testnet API Key set')

            if message.text.startswith('api secret testnet '):
                self.main_bot.config['binance_api_secret_testnet'] = message.text[19:]
                self.main_bot.save_state()
                self.telebot.reply_to(message, 'Testnet API Secret set')

            # When all keys are provided

            if self.main_bot.keys_ready():

                if message.text.startswith('set '):
                    arguments = message.text[4:].split()
                    try:
                        if self.main_bot.streams_running:
                            self.telebot.send_message(message.from_user.id, 'Stop streams before starting a new configuration')
                        else:
                            self.parse_stream_args(*arguments)
                            self.main_bot.setup_streams()
                            self.telebot.send_message(message.from_user.id, 'Streams configured')
                    except Exception as err:
                        self.telebot.reply_to(message, err.message)

                if message.text.startswith('start '):
                    arguments = message.text[6:].split()
                    try:
                        if self.main_bot.streams_running:
                            self.telebot.send_message(message.from_user.id, 'Stop streams before starting a new configuration')
                        else:
                            self.parse_stream_args(*arguments)
                            self.main_bot.setup_streams()
                            self.telebot.send_message(message.from_user.id, 'Streams configured')
                            self.main_bot.run_streams()
                            self.telebot.send_message(message.from_user.id, 'Streams started at\n {}'.format(dt.datetime.now().strftime("%d-%m-%Y %H:%M")))
                    except Exception as err:
                        self.telebot.reply_to(message, err.message)

                if message.text == 'start':
                    try:
                        if self.main_bot.streams_running:
                            self.telebot.send_message(message.from_user.id, 'Streams already running')
                        else:
                            if self.main_bot.config_ready():
                                self.main_bot.run_streams()
                                self.telebot.send_message(message.from_user.id, 'Streams started at\n {}'.format(dt.datetime.now().strftime("%d-%m-%Y %H:%M")))
                            else:
                                self.telebot.reply_to(message, 'No streams have been configured yet')
                    except Exception as err:
                        self.telebot.reply_to(message, err.message)

                if message.text == 'stop':
                    try:
                        if not self.main_bot.streams_running:
                            self.telebot.send_message(message.from_user.id, 'Streams stopped already')
                        else:
                            self.main_bot.stop_streams()
                            self.telebot.send_message(message.from_user.id, 'Streams stopped')
                    except Exception as err:
                        self.telebot.reply_to(message, err.message)

                if message.text.startswith('dollar '):
                    dollar = message.text[7:]
                    if (
                        dollar == 'USDT' or 
                        dollar == 'USDC'
                    ):
                        self.main_bot.config['dollar'] = dollar
                    else:
                        self.telebot.reply_to(message, 'The currency is not valid. Call either "dollar USDT" or "dollar USDC"')

                if message.text.startswith('testnet '):
                    testnet = message.text[8:].title()
                    if self.main_bot.streams_running:
                        self.telebot.reply_to(message, 'Streams must be stopped before changing Testnet state')
                    else:
                        if testnet == 'True':
                            if not self.main_bot.config['testnet']:
                                self.main_bot.config['testnet'] = True
                                self.main_bot.save_state()
                                self.main_bot.start_api_client()
                            self.telebot.send_message(message.from_user.id, 'Testnet set to True')
                        elif testnet == 'False':
                            if self.main_bot.config['testnet']:
                                self.main_bot.config['testnet'] = False
                                self.main_bot.save_state()
                                self.main_bot.start_api_client()
                            self.telebot.send_message(message.from_user.id, 'Testnet set to False')
                        else:
                            self.telebot.reply_to(message, 'Invalid command. Call either "testnet True" or "testnet False"')

                if message.text == 'config':
                    config_msg = """
Markets : {}
Intervals : {}
Strategies : {}
Sizers : {}
Start Qties : {}
Testnet : {}
Dollar : {}
                    """.format(
                        self.main_bot.config['markets'],
                        self.main_bot.config['intervals'],
                        self.main_bot.config['strategies'],
                        self.main_bot.config['sizers'],
                        self.main_bot.config['start_qties'],
                        self.main_bot.config['testnet'],
                        self.main_bot.config['dollar'],
                    )
                    self.telebot.send_message(message.from_user.id, config_msg)

                if message.text.startswith('stream'):

                    stream_args = message.text.split()

                    if len(stream_args) == 1:
                        stream_names = 'Running streams : \n'
                        for stream in self.main_bot.streams:
                            stream_names += stream.name + '\n'
                        self.telebot.send_message(message.from_user.id, stream_names)

                    if len(stream_args) == 2:

                        if (
                            stream_args[1].lower() == 'profits'
                        ):
                            streams_profits = self.main_bot.streams.profits()
                            streams_profits_msg = """
Total Stake : {}$
Current Value : {}$
Total Profit : {}$ ({}%)
                            """.format(
                                streams_profits['total_stake'],
                                streams_profits['current_value'],
                                streams_profits['overall_profit'],
                                streams_profits['total_profit_percent']
                            )
                            self.telebot.send_message(message.from_user.id, streams_profits_msg)

                    if len(stream_args) == 3:
                        
                        if (
                            stream_args[2].upper() == 'BUY' or
                            stream_args[2].upper() == 'SELL'
                            ):
                                if self.main_bot.streams_running:
                                    try:
                                        self.main_bot.stream_order(stream_args[1], stream_args[2])
                                    except Exception as err:
                                        self.telebot.reply_to(message, err.message)
                                else:
                                    self.telebot.reply_to(message, 'Streams must be running to make an order')

                        if (
                            stream_args[2].lower() == 'profits'
                        ):
                            for stream in self.main_bot.streams:
                                if stream.name == stream_args[1].lower():
                                    stream_profits_msg = """
{}
Stake : {}$
Current Value : {}$
Last trade profit : {}$
Total stream profit : {}$ ({}%)
                                    """.format(
                                        stream.name,
                                        stream.strategy.orders[0]['usd'] if stream.strategy.orders else 0.0,
                                        stream.strategy.orders[-1]['usd'] if stream.strategy.orders else 0.0,
                                        '%.2f' % stream.strategy.trade_profit,
                                        '%.2f' % stream.strategy.total_profit,
                                        '%.2f' % stream.strategy.total_profit*100.0/stream.strategy.orders[0]['usd'] if stream.strategy.orders else 0.0
                                    )
                                    self.telebot.send_message(message.from_user.id, stream_profits_msg)
                    


            else:
                missing_keys_message = 'Please provide all keys before continuing\nMissing keys : \n'
                if not self.main_bot.config['binance_api_key']:
                    missing_keys_message += 'api key\n'
                if not self.main_bot.config['binance_api_secret']:
                    missing_keys_message += 'api secret\n'
                if not self.main_bot.config['binance_api_key_testnet']:
                    missing_keys_message += 'api key testnet\n'
                if not self.main_bot.config['binance_api_secret_testnet']:
                    missing_keys_message += 'api secret testnet\n'
                self.telebot.reply_to(message, missing_keys_message)

            if self.main_bot.keys_ready() and not self.main_bot.api_client_running:
                self.main_bot.start_api_client()

            

    def parse_stream_args(self, *args):
        
        if len(args)%5==0:
            markets = [a.lower() for a in args[0::5]]
            intervals = [a.lower() for a in args[1::5]]
            strats = [a.lower() for a in args[2::5]]
            sizrs = [a.lower() for a in args[3::5]]
            start_qties = [float(a) for a in args[4::5]]
        else:
            raise exc.WrongArgFormat

        self.main_bot.config['markets'] = list(m + self.main_bot.config['dollar'].lower() for m in markets)

        for interval in intervals:
            if not data.INTERVAL_VALUES.count(interval):
                raise exc.WrongIntervalFormat
        self.main_bot.config['intervals'] = intervals

        from .strategybase import StrategyBase
        from . import strategies
        if are_subclass_of(strats, StrategyBase):
            self.main_bot.config['strategies'] = strats
        else:
            raise exc.StrategyNotFound

        from .sizerbase import SizerBase
        from . import sizers
        if are_subclass_of(sizrs, SizerBase):
            self.main_bot.config['sizers'] = sizrs
        else:
            raise exc.SizerNotFound

        self.main_bot.config['start_qties'] = start_qties



    def start(self):

        self.telebot_thread = threading.Thread(target=self.telebot.infinity_polling)
        self.telebot_thread.start()

    def stop(self):

        if self.main_bot.streams_running:
            self.main_bot.stop_streams()
            self.main_bot.streams_running = False

        self.main_bot.save_state()

        self.telebot.send_message(self.main_bot.config['telegram_user_id'], "Bot successfully stopped")
        
        self.telebot.stop_bot()
        self.telebot_thread.join()