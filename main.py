import core 
import time

core.init(False, 'BTCUSD0624', '1')
print(core.get_balance())
my_price = core.get_price()

r = core.create_order("Buy", 1, my_price - 1000, True)
print(r)
time.sleep(1)
r = core.create_order("Sell", 1, my_price + 1000, True)
print(r)