import datetime as dt
from os import system

def format_rows(rows: list, width=15) -> str:
    ret = ''
    for row in rows:
        row_format = "{:<15}" * (len(row)+1)
        ret += row_format.format('', *row) + '\n'
    return ret

def bot_display():
    from .stream import _streams_global_access as _sga

    system('clear')

    overall_profit = 0.0
    total_stake = 0.0
    total_profit_percent = 0.0

    for stream in _sga:

        print(stream)
        print(stream.strategy)
        print(stream.strategy.sizer)

        if stream.strategy.orders:
            total_stake += stream.strategy.orders[0]['usd']
            
        overall_profit += stream.strategy.total_profit

    if total_stake != 0:
        total_profit_percent = overall_profit / total_stake

    rows = []
    rows.append(['Total Stake','Total Profit', '%'])
    rows.append([
        str(total_stake) + '$',
        str(overall_profit) + '$',
        f"{total_profit_percent}%"
    ])

    print(format_rows(rows))