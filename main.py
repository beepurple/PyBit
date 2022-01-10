import core 
import time
from Order import Order

core.init(False, 'BTCUSD0624', '1')
print(core.get_balance())
my_price = core.get_price()

o1 = Order('B1', True)

o1.create_order(1, my_price - 1000)

print(o1.order_id)
time.sleep(1)

o2 = Order('S1', False)
o2.create_order(1, my_price + 1000)
print(o2.order_id)