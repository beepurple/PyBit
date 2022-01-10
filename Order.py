import core

class Order:
    def __init__(self, _name, _side):
        self.name = _name
        self.side = _side
    
    def set_side(self):
        return 'Buy' if self.side else 'Sell'
    
    def create_order(self, _qty, _price):
        side = self.set_side()
        self.order_id = core.create_order(side, _qty, _price, True)