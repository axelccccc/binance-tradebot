from .sizerbase import SizerBase



class SizerFix(SizerBase):
    def __init__(self, owner):

        super(SizerFix, self).__init__(owner)

    def resize_buy(self) -> float:
        self.strategy.qty = self.format_qty(self.strategy.qty)

    def resize_sell(self) -> float:
        self.strategy.qty = self.format_qty(self.strategy.qty)

    def info(self) -> dict:
        return {
            'name': 'Fix',
            'params': {
                'Stake': self.strategy.qty
            }
        }


class SizerPercent(SizerBase):
    def __init__(self, owner, percentage=99.9):

        self.percentage = percentage

        super(SizerPercent, self).__init__(owner)

    def resize_buy(self) -> float:
        new_qty = self.strategy.orders[-1]['usd'] * (self.percentage/100.0) / self.close_values[-1]
        self.strategy.qty = self.format_qty(new_qty)

    def resize_sell(self) -> float:
        self.strategy.qty = self.format_qty(self.strategy.qty)

    def info(self) -> dict:
        return {
            'name': 'Percent',
            'params': {
                'Percentage': f'{self.percentage}%'
            }
        }

    
    