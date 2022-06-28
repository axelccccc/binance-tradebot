# binance-tradebot

Binance TradeBot is a live SPOT trading bot for [Binance](https://www.binance.com/), controlled through [Telegram](https://telegram.org).
It supports parallel trading over multiple markets, each using a strategy and timeframe of their own.



Installation
============

> The program is untested with a python version inferior to 3.7.

```
git clone https://github.com/axelccccc/binance-tradebot.git
```
It is strongly advised to install and use the program in a separate environment (venv, conda, etc.).
Once in your environment : 
```
pip install -r requirements.txt
```

## First Launch

In your environment : 
```
python main.py
```

On first launch, you will be asked for your Telegram bot ID and user ID.
To create a Telegram bot and get the bot ID, send `/start` to `@BotFather` on Telegram and follow the instructions.
To get your Telegram user ID, send `/start` to `@userinfobot` on Telegram.

Once this is done, you should have received a message telling you the bot is started.

Now you can provide your Binance API keys my sending to your bot as messages, one at a time : 
```
api key <key>
api secret <secret>
api key testnet <key>
api secret testnet <secret>
```

Once all the keys have been provided, you will be able to use the common commands to control the bot.



Usage
=====

Those commands are sent to the bot directly from the Telegram chat.

## Configuring a new trading stream

```
set <currency> <interval> <strategy> <sizer> <start qty>
```

To understand strategies and sizers, see the following sections

The bot currently trades between the specified currency and a dollar stablecoin.
By default, the stablecoin is USD Tether ($USDT).
To change the stablecoin used
```
dollar <USDT/USDC>
```

You can then disable or activate testnet
```
testnet <true/false>
```

Preview your settings before launch and during trading
```
config
```

## Starting and stopping a stream

Start the last configured stream
```
start
```

Start a new configuration on the fly
```
start <currency> <interval> <strategy> <sizer> <start qty>
```

> Don't forget to have your dollar stablecoin and tesnet setting set up properly !

Stop the stream
```
stop
```

## Stream statistics and actions

Preview running streams
```
stream
```

You can then use the given stream names to get information or act on the stream.


See the profit/loss made on the current total stake
```
stream profits
```

See more precise information on a stream
```
stream <stream name> profits
```

Buy/sell independently of the bot's decision at any given time
```
stream <stream name> <BUY/SELL>
```



Strategies
==========

Strategies are user-defined algorithms based on a variety of financial and mathematical indicators, used in real time by the bot to take decisions on whether to buy or sell the asset.

You can define a new one by creating a subclass to `StrategyBase` in your `main.py` file. You will be able to call it from the Telegram interface by the same name you gave it in the code.

Here is an example

```python
class BasicRSI(StrategyBase):

    """You can define as construction arguments custom parameters with default values"""
    
    def __init__(self, owner, sizer, rsi_period=14, rsi_oversold=30, rsi_overbought=70) -> None:
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.rsi = []

        super(BasicRSI, self).__init__(owner, sizer)


    def longest_period(self) -> int:
        """This method should return the longest number of intervals
        required by an indicator in use to produce its first correct value.
        This number of past intervals is then retrieved to produce the 
        first values for each indicator.
        """

        return self.rsi_period

    def start(self):
        """This method is launched right before starting trading.
        It is here used to get the close values into a numpy array, to be
        used by the TALib's RSI indicator.
        """

        self.np_closes = numpy.array(self.stream.close_values)
        self.rsi = talib.RSI(self.np_closes, self.rsi_period)

    def next(self) -> None:
        """This method defines the action taken each time an interval is closed.
        It is here that the buying and selling actions take place.
        """

        if len(self.stream.close_values) >= self.rsi_period:

            self.np_closes = numpy.array(self.stream.close_values)
            self.rsi = talib.RSI(self.np_closes, self.rsi_period)

            if (
                self.rsi[-1] > self.rsi_overbought and 
                self.position
            ):
                self.sell()
            elif (
                self.rsi[-1] < self.rsi_oversold and 
                not self.position
            ):
                self.buy()

    def info(self) -> dict:
        """This method allows for display of strategy information at the command line during execution
        """
        strat_info = {
            'name': 'Basic RSI',
            'params': {
                'RSI': (round(self.rsi[-1],2) if len(self.rsi) else 0.0),
                'RSI Period': self.rsi_period,
                'RSI Overbought': self.rsi_overbought,
                'RSI Oversold': self.rsi_oversold
            }
        }
        return strat_info
```



Sizers
======

Sizers are a way to calculate what asset quantity is used at each trade.

You can define a new one by creating a subclass to `SizerBase` in your `main.py` file. You will be able to call it from the Telegram interface by the same name you gave it in the code.

The `sizer.py` files contains basic ones you can use as is or as a reference.