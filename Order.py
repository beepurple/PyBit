import core
import time
import pprint as pp
class Order:
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
    
    def set_side(self):
        return 'Buy' if self.side else 'Sell'
    
    def set_order(self, _qty, _price, _status, _filled=False):
        if _filled:
            self.side = not self.side
            self.close = not self.close

        if self.close:
            self.close_price = float(_price)
        else:
            self.open_price = float(_price)
        
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
                result = core.get_order_status(self.order_id)
                status = result['order_status']                
                done = True
                
            except Exception as e:
                print("get_order_status error...", result, e)
                time.sleep(1)
                
        self.order_status = status
        if status == 'New' and checkNew:
            self.set_order(result['qty'], result['price'], status)
            print(self.name, self.side, self.close, result['qty'], result['price'], "주문이 정상 진입하였습니다.",
                  core.get_cur_time(), "현재 Step:", self.step)
            
            if self.step == 1:
                self.step = 2
            elif self.step == 3:
                self.step = 4

        elif status == 'Filled':
            print(self.name, result['side'], self.close, result['qty'], result['price'], "거래가 체결 되었습니다.", "현재 Step:", self.step)
            if self.close:
                rst = (self.open_price - self.close_price) if self.side else (self.close_price - self.open_price)
                if 0 < rst:
                    self.win += 1
                else:
                    self.lose += 1
                self.total_profit += (rst / core.cur_price)

                print(self.name, "win :", self.win, "lose :", self.lose, "이득 금액", rst, self.total_profit, "현재 Step:", self.step)
            
            if self.step == 2:
                self.step = 3
            elif self.step == 4:
                self.step = 5

            self.set_order(result['qty'], result['price'], status, True)

        elif status == 'Cancelled':
            if self.step == 2:
                self.step = 1
            elif self.step == 4:
                self.step = 3
            print(self.name, self.side, self.close, "Cancelled!!", "현재 Step:", self.step)
            done = False
        # elif status == 'Created':
        #     done = False
        # elif status == 'PendingCancel' or status == 'Rejected':
        #     done = False
        else:
            done = False

        return done, status
    
    def create_order(self, _price='', _qty=''):
        done = False
        status = ''

        if _price == '':
            _price = self.open_price
            if self.close:
                _price += 100 * (-1 if self.side else 1)

        if _qty == '':
            _qty = self.qty

        while not done:
            if status != 'Created':
                side = self.set_side()
                self.order_id = core.create_order(side, _qty, _price, self.close)
            done, status = self.get_order_status()

    def cancel_order(self):
        result = core.cancel_order(self.order_id)
        time.sleep(0.01)
        return result 
    
    def change_order_price(self, r_price):
        self.cancel_order()
        self.create_order(r_price)

