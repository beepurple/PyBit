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

# core.get_my_position()
# pp.pprint(core.my_pos)
# print(core.my_pos[1]['unrealised_pnl'], core.my_pos[2]['unrealised_pnl'])

print("pnl0 = ", core.get_pnl())
print("pnl1 = ", core.get_pnl(1))
print("pnl2 = ", core.get_pnl(2))
#print((core.my_pos[1]['position_value'] + core.my_pos[2]['position_value']) / (core.my_pos[0]['position_value'] * margin) * 100)

order = [[], []]
total_size = 5
tick_size = 50
for i in range(total_size):
    o = Order(str(i) + 'B', True)
    order[0].append(o)
    o = Order(str(i) + 'S', False)
    order[1].append(o)


done = False
while done:
    time.sleep(2)
    core.cur_price = core.get_price()
    for i in range(2):
        price = core.cur_price
        tick = tick_size
        for o in order[i]:
            if o.step == 0:
                
                o.open_price = price + (tick * (-1 if o.side else 1))
                tick += tick_size
                o.qty = 1
                o.step = 1
                
            elif o.step == 1:
                o.create_order()

            elif o.step == 2:
                Filled, _ = o.get_order_status(False)
                
                if Filled:
                    print("변경 합니다.")    
                    for ro in order[1-i]:
                        if ro.step == 2:
                            ro.change_order_price(ro.open_price - tick_size *(-1 if ro.side else 1))

            elif o.step == 3:
                o.create_order()
            elif o.step == 4:
                o.get_order_status(False)
            elif o.step == 5:
                done = False

                