from .gui import format_rows


class SizerBase():
    def __init__(self, owner):
        self.strategy = owner
    
    @property
    def close_values(self):
        return self.strategy.close_values

    def resize(self) -> float:
        pass

    def info(self) -> dict:
        return {
            'name': '',
            'params': {}
        }

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


class SizerFix(SizerBase):
    def __init__(self, owner):

        super(SizerFix, self).__init__(owner)

    def info(self) -> dict:
        return {
            'name': 'Fix',
            'params': {
                'Stake': self.strategy.qty
            }
        }

    def resize(self) -> float:
        pass

class SizerPercent(SizerBase):
    def __init__(self, owner, percentage=99.0):

        self.percentage = percentage

        super(SizerPercent, self).__init__(owner)

    def info(self) -> dict:
        return {
            'name': 'Fix',
            'params': {
                'Percentage': f'{self.percentage}%'
            }
        }

    def resize(self) -> float:
        self.strategy.qty = self.strategy.orders[-1]['usd'] * (self.percentage/100.0) / self.close_values[-1]
    
    