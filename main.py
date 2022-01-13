import core 
import time
from Order import Order
import pprint as pp

margin = 10
testnet = False
symbol = 'BTCUSD0624'
core.init(testnet, symbol, margin)

balance = core.get_balance()
my_price = core.get_price()


# o1 = Order('B1', True)

# o1.open_order(my_price - 50)

# # print(o1.order_id)
# # time.sleep(1)

# o2 = Order('S1', False)
# o2.open_order(my_price + 50)
# print(o2.order_id)

#core.create_order("Buy", 1, 43500, False)

#pp.pprint(core.get_order_status())

core.get_my_position()

pp.pprint(core.my_pos)

print((core.my_pos[1]['value'] + core.my_pos[2]['value']) / (core.my_pos[0]['value'] * margin) * 100)

order = [[], []]
total_size = 2
for i in range(total_size):
    o = Order(str(i) + 'B', True)
    order[0].append(o)
    o = Order(str(i) + 'S', False)
    order[1].append(o)

while False:
    core.cur_price = core.get_price()
    for i in range(2):
        for o in order[i]:
            if o.step == 0:
                
                o.price = 1
                o.qty = 1
                print(o.name, "생성 합니다.")
            elif o.step == 1:
                o.open_order()
