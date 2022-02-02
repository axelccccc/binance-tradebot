from . import data
from . import socket
from . import exceptions as exc
from .telegram import ThreadedTelegramHandler
from .stream import Streams



# Main bot class to encapsulate everything

class TradeBot():
    def __init__(self, bot_token: str = None, user_id: int = None):

        self.config = data.load_config()

        self.streams_running = False
        self.api_client_running = False


        if bot_token:
            self.config['telegram_bot_token'] = bot_token
        elif not self.config['telegram_bot_token']:
            #raise exc.NoTelegramBotToken
            t_bot_token = input('Enter Telegram Bot Token : ')
            self.config['telegram_bot_token'] = t_bot_token

        if user_id:
            self.config['telegram_user_id'] = user_id
        elif not self.config['telegram_user_id'] or self.config['telegram_user_id'] == 0:
            #raise exc.NoTelegramUserID
            t_bot_user_id = input('Enter Telegram User ID : ')
            self.config['telegram_user_id'] = int(t_bot_user_id)

        self.save_state()

        self.t_bot = ThreadedTelegramHandler(self, self.config['telegram_bot_token'])

        if self.keys_ready():
            self.start_api_client()

        if self.config_ready():
            self.setup_streams()

    # Data

    def save_state(self):
        data.save_data(self.config, data.CONFIG_PATH, 'w')

    # Config Flags

    @property
    def testnet(self):
        return self.config['testnet']

    def keys_ready(self) -> bool:
        return (
            self.config['telegram_bot_token'] and 
            self.config['telegram_user_id'] and 
            self.config['binance_api_key'] and 
            self.config['binance_api_key_testnet'] and 
            self.config['binance_api_secret'] and 
            self.config['binance_api_secret_testnet']
        )

    def config_ready(self) -> bool:
        for param in self.config.values():
            if not param and type(param) != bool:
                return False
        return True

    # Startup

    def start_api_client(self):

        self.api_client_running = False

        from . import api

        if self.testnet:
            api._cga = api.APIClient(
                self,
                self.config['binance_api_key_testnet'],
                self.config['binance_api_secret_testnet'],
                testnet=True
            )
        else:
            api._cga = api.APIClient(
                self,
                self.config['binance_api_key'],
                self.config['binance_api_secret'],
                testnet=False
            )
        
        self.api_client = api._cga

        self.api_client_running = True

    def setup_websocket(self):

        if not self.config_ready():
            raise exc.BotNotConfigured

        if not (self.api_client and self.streams):
            raise exc.MissingClientOrStreams

        self.ws = socket.WebSocketClient(self)

    def setup_streams(self):
        if self.config_ready():
            self.streams = Streams(self.config)
            self.setup_websocket()
            self.save_state()
        else:
            raise exc.BotNotConfigured

    def run_streams(self):
        if self.streams:
            self.ws.run()
            self.streams_running = True
        else:
            if self.config_ready():
                self.setup_streams()
                self.ws.run()
                self.streams_running = True
            else:
                raise exc.BotNotConfigured

    def stop_streams(self):
        self.ws.stop()
        self.streams_running = False

    # def restart_streams(self):
    #     self.ws.stop()
    #     self.streams_running = False
    #     self.run_streams()
    #     self.streams_running = True

    def start(self):
        self.t_bot.start()

    def stop(self):
        self.t_bot.stop()

    # Individual actions

    def stream_order(self, name, side):
        if self.streams:
            for stream in self.streams:
                if stream.name.lower() == name.lower():
                    if (
                        (stream.strategy.position and side.upper() == 'SELL') or 
                        (not stream.strategy.position and side.upper() == 'BUY')
                    ):
                        stream.strategy.order(side.upper())
                        return
                    else:
                        raise exc.MatchedPosition
            raise exc.NoStreamWithName
        else:
            raise exc.MissingClientOrStreams
    
    def stream_buy(self, symbol):
        self.stream_order(symbol, 'BUY')

    def stream_sell(self, symbol):
        self.stream_order(symbol, 'SELL')