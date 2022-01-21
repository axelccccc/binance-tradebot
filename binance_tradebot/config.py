from . import private
from . import exceptions as exc
from .utils import are_subclass_of

########## CONFIG OPTIONS ##########

TESTNET = True

MARKETS = ['btcusdt']

INTERVALS = ['1m']

START_TRADE_QTIES = [0.0]

STRATEGIES = ['BasicRSI']

SIZERS = ['SizerFix']

DOLLAR = 'USDT'

####################################

bot_is_configured = False

DATA_PATH = 'data/'

if TESTNET:

    USER_INFO_PATH = DATA_PATH + 'test_user_info.json'
    ORDERS_DATA_PATH = DATA_PATH + 'test_orders.json'
    API_KEY = private.API_KEY_TESTNET
    API_SECRET = private.API_SECRET_TESTNET

else:

    USER_INFO_PATH = DATA_PATH + 'user_info.json'
    ORDERS_DATA_PATH = DATA_PATH + 'orders.json'
    API_KEY = private.API_KEY
    API_SECRET = private.API_SECRET

INTERVAL_VALUES = ('1m','3m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','3d','1w','1M')



def set_config(*args, testnet=False, dollar='USDT'):
    """
    Set configuration variables to run the program.

    :param *args: 
    Format : CUR ITV STRAT SIZ QTY CUR ITV STRAT SIZ QTY ... \n
    CUR : (str) Currencies to trade \n
    ITV : (str) Candlestick interval \n
    STRAT : (str) Strategy to be used \n
    SIZ : (str) Sizer to be used \n
    QTY : (float) Corresponding starting quantity \n
    Raises an exception if not enough cash is available to start (USDT)

    :param testnet: 
    Whether the bot is run on the Binance testnet network 
    or directly in live trading.

    :param dollar:
    Dollar coin used for cash & markets : Either 'USDT' or 'USDC'
    """
    
    global TESTNET
    global MARKETS
    global INTERVALS
    global START_TRADE_QTIES
    global STRATEGIES
    global SIZERS
    global DOLLAR
    global bot_is_configured



    if dollar.upper() == 'USDT' or dollar.upper() == 'USDC':
        DOLLAR = dollar.upper()
    else:
        raise exc.WrongCashCurrency
    


    if len(args)%5==0:
        markets = [args[a].lower() for a in range(0, len(args)) if a%5==0]
        intervals = [args[a].lower() for a in range(0, len(args)) if a%5==1]
        strategies = [args[a].lower() for a in range(0, len(args)) if a%5==2]
        sizers = [args[a].lower() for a in range(0, len(args)) if a%5==3]
        start_qties = [args[a] for a in range(0, len(args)) if a%5==4]
    else:
        raise exc.WrongArgFormat

    MARKETS = list(m + DOLLAR.lower() for m in markets)

    for interval in intervals:
        if not INTERVAL_VALUES.count(interval):
            raise exc.WrongIntervalFormat
    INTERVALS = intervals

    from .strategy import StrategyBase
    if are_subclass_of(strategies, StrategyBase):
        STRATEGIES = strategies
    else:
        raise exc.StrategyNotFound

    from .sizer import SizerBase
    if are_subclass_of(sizers, SizerBase):
        SIZERS = sizers
    else:
        raise exc.SizerNotFound

    # Add something to check there is enough cash to trade all starting quantities ?
    START_TRADE_QTIES = start_qties

    TESTNET = testnet

    bot_is_configured = True