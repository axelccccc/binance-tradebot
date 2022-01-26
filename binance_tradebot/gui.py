from os import system

def format_rows(rows: list, width=15) -> str:
    ret = ''
    for row in rows:
        row_format = "{:<15}" * (len(row)+1)
        ret += row_format.format('', *row) + '\n'
    return ret

def bot_display():
    from .stream import _sga

    system('clear')

    for stream in _sga:

        print(stream)
        print(stream.strategy)

    streams_profits = _sga.profits()

    rows = []
    rows.append(['Total Stake', 'Current Val.', 'Total Profit', '%'])
    rows.append([
        f"{streams_profits['total_stake']}$",
        f"{streams_profits['current_value']}$",
        f"{streams_profits['overall_profit']}",
        f"{streams_profits['total_profit_percent']}%"
    ])

    print(format_rows(rows))