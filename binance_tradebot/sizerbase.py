from .gui import format_rows
from math import floor


class SizerBase():
    def __init__(self, owner):
        self.strategy = owner
        self.get_step_size()
    
    @property
    def close_values(self):
        return self.strategy.stream.close_values

    def resize_buy(self) -> float:
        pass

    def resize_sell(self) -> float:
        pass

    def info(self) -> dict:
        return {
            'name': '',
            'params': {}
        }

    def get_step_size(self):
        from .api import _cga
        symbol_info = _cga.client.get_symbol_info(self.strategy.stream.symbol)
        for f in symbol_info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                self.step_size = f['stepSize']

    def format_qty(self, qty):
        return self._format_value(qty, self.step_size)

    def _format_value(self, value, step):
        precision = step.find('1') - 1
        if precision > 0:
            return float('{:0.0{}f}'.format(value, precision))
        return floor(int(value))

    def __str__(self):

        info = self.info()
        
        rows = []
        rows.append(['Sizer : ' + info['name']])
        h_sizer_sliced = []
        r_sizer_sliced = []
        for param, value in info['params'].items():
            if len(h_sizer_sliced) == 5:
                rows.append(h_sizer_sliced)
                rows.append(r_sizer_sliced)
                h_sizer_sliced = []
                r_sizer_sliced = []
            h_sizer_sliced.append(param)
            r_sizer_sliced.append(value)
        rows.append(h_sizer_sliced)
        rows.append(r_sizer_sliced)
        
        return format_rows(rows)