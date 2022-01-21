# Config Setup Exceptions

class WrongCashCurrency(Exception):
    def __init__(self):
        message = "Wrong cash currency. Must either be USDT or USDC"
        super().__init__(message)

class WrongArgFormat(Exception):
    def __init__(self):
        message = "Wrong argument format. Format is CUR ITV STRAT SIZ QTY CUR ITV STRAT SIZ QTY ..."
        super().__init__(message)

class WrongIntervalFormat(Exception):
    def __init__(self):
        message = "Wrong interval format."
        super().__init__(message)

class StrategyNotFound(Exception):
    def __init__(self):
        message = "Strategy not found or inexistent."
        super().__init__(message)

class SizerNotFound(Exception):
    def __init__(self):
        message = "Sizer not found or inexistent."
        super().__init__(message)

class NotEnoughCash(Exception):
    def __init__(self):
        message = "Not enough starting cash in account."
        super().__init__(message)



# Streams Exceptions

class BotNotConfigured(Exception):
    def __init__(self):
        message = "The bot was not properly configured. Streams cannot be created"
        super().__init__(message)

class MoreThanOneAggregate(Exception):
    def __init__(self):
        message = "There can be only one streams aggregate per program run."
        super().__init__(message)



# Socket Exceptions

class MissingClientOrStreams(Exception):
    def __init__(self):
        message = "Stream(s) and/or API client missing (not instantiated)"
        super().__init__(message)