# Config Setup Exceptions

class NoTelegramBotToken(Exception):
    def __init__(self):
        self.message = "Telegram bot token is missing."
        super().__init__(self.message)

class NoTelegramUserID(Exception):
    def __init__(self):
        self.message = "Telegram user ID is missing."
        super().__init__(self.message)

class WrongCashCurrency(Exception):
    def __init__(self):
        self.message = "Wrong cash currency. Must either be USDT or USDC"
        super().__init__(self.message)

class WrongArgFormat(Exception):
    def __init__(self):
        self.message = "Wrong argument format. Format is CUR ITV STRAT SIZ QTY CUR ITV STRAT SIZ QTY ..."
        super().__init__(self.message)

class WrongIntervalFormat(Exception):
    def __init__(self):
        self.message = "Wrong interval format."
        super().__init__(self.message)

class StrategyNotFound(Exception):
    def __init__(self):
        self.message = "Strategy not found or inexistent."
        super().__init__(self.message)

class SizerNotFound(Exception):
    def __init__(self):
        self.message = "Sizer not found or inexistent."
        super().__init__(self.message)

class NotEnoughCash(Exception):
    def __init__(self):
        self.message = "Not enough starting cash in account."
        super().__init__(self.message)



# Streams Exceptions

class BotNotConfigured(Exception):
    def __init__(self):
        self.message = "The bot was not properly configured. Streams cannot be created"
        super().__init__(self.message)

class MoreThanOneAggregate(Exception):
    def __init__(self):
        self.message = "There can be only one streams aggregate per program run."
        super().__init__(self.message)

class NoStreams(Exception):
    def __init__(self):
        self.message = "No streams found."
        super().__init__(self.message)

class NoStreamWithName(Exception):
    def __init__(self):
        self.message = "No streams found with this name. \nSend 'stream' to get the list of available streams"
        super().__init__(self.message)

class MatchedPosition(Exception):
    def __init__(self):
        self.message = "Order could not proceed — matched strategy position."
        super().__init__(self.message)




# Socket Exceptions

class MissingClientOrStreams(Exception):
    def __init__(self):
        self.message = "Stream(s) and/or API client missing (not instantiated)"
        super().__init__(self.message)