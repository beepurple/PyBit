
import time
import pprint as pp
class Order:
    open_last_price = [float('inf'), 0.0]
    close_last_price = [0.0, float('inf')]
    core = ''

    def __init__(self, _name, _side):
        self.name = _name
        self.side = _side
        self.qty = 1
        self.open_price = 0.0
        self.close_price = 0.0
        self.close = False
        self.order_status = ''
        self.order_id = ''
        self.time = 0.0
        self.step = 0

        self.win = 0
        self.lose = 0
        self.total_profit = 0.0
    
    def set_side(self):
        return 'Buy' if self.side else 'Sell'
    
    def set_order(self, _qty, _price, _status, _filled=False):
        if _filled:
            self.side = not self.side
            self.close = not self.close

        if self.close:
            self.close_price = float(_price)
            if self.side:
                if self.close_price < Order.close_last_price[1]:
                    Order.close_last_price[1] = self.close_price
            else:
                if Order.close_last_price[0] < self.close_price:
                    Order.close_last_price[0] = self.close_price
        else:
            self.open_price = float(_price)
            if self.side:
                if self.open_price < Order.open_last_price[0]:
                    Order.open_last_price[0] = self.open_price
            else:
                if Order.open_last_price[1] < self.open_price:
                    Order.open_last_price[1] = self.open_price
        
        self.order_status = _status
        
        self.qty = float(_qty)        
        self.time = float(time.time())
    
    def get_order_status(self, checkNew=True):
        result = []
        done = False
        status = ''
        if self.order_id == '':
            return done, status 
        
        while not done:
            try:
                result = Order.core.get_order_status(self.order_id)
                status = result['order_status']                
                done = True
                
            except Exception as e:
                print("get_order_status error...", result, e)
                time.sleep(1)
                
        self.order_status = status
        if status == 'New' and checkNew:
            self.set_order(result['qty'], result['price'], status)
            print(self.name, self.side, self.close, result['qty'], result['price'], "????????? ?????? ?????????????????????.",
                  Order.core.get_cur_time(), "?????? Step:", self.step)
            
            if self.step == 1:
                self.step = 2
            elif self.step == 3:
                self.step = 4

        elif status == 'Filled':
            print(self.name, result['side'], self.close, result['qty'], result['price'], "????????? ?????? ???????????????.", "?????? Step:", self.step)
            if self.close:
                rst = (self.open_price - self.close_price) if self.side else (self.close_price - self.open_price)
                if 0 < rst:
                    self.win += 1
                else:
                    self.lose += 1
                self.total_profit += (rst / Order.core.cur_price)

                print(self.name, "win :", self.win, "lose :", self.lose, "?????? ??????", rst, self.total_profit, "?????? Step:", self.step)
            
            if self.step == 2:
                self.step = 3
            elif self.step == 4:
                self.step = 0

            self.set_order(result['qty'], result['price'], status, True)

        elif status == 'Cancelled':
            if self.step == 2:
                self.step = 1
            elif self.step == 4:
                self.step = 3
            print(self.name, self.side, self.close, "Cancelled!!", "?????? Step:", self.step)
            done = False
        # elif status == 'Created':
        #     done = False
        # elif status == 'PendingCancel' or status == 'Rejected':
        #     done = False
        else:
            done = False

        return done, status
    
    def create_order(self, _price='', _qty='', _tick=100):
        done = False
        status = ''

        my_side = -1 if self.side else 1
        if _price == '':
            _price = self.open_price
            if self.close:
                _price += _tick * my_side

        if _qty == '':
            _qty = self.qty

        while not done:
            if status != 'Created':
                side = self.set_side()
                self.order_id = Order.core.create_order(side, _qty, _price, self.close)
            done, status = self.get_order_status()

            check = False
            if self.close:
                if self.side:
                    if Order.core.cur_price < _price:
                        check = True
                else:
                    if _price < Order.core.cur_price:
                        check = True 

                if check:
                    _price = Order.core.cur_price + (_tick * my_side)   
                else:
                    _price += (_tick * my_side) 

    def cancel_order(self):
        result = Order.core.cancel_order(self.order_id)
        time.sleep(0.01)
        return result 
    
    def change_order_price(self, r_price):
        self.cancel_order()
        self.create_order(r_price)

