from json.encoder import INFINITY
from Core import Core
import time
from Order import Order
import pprint as pp

margin = 10
testnet = False
symbol = 'BTCUSD0624'
core = Core(testnet, symbol, margin)

balance = core.get_balance()
my_price = core.get_price()


tot_val = core.get_total_qty() * margin
order = [[], []]

qty_size = 1
# if tot_val > total_size:
#     qty_size = tot_val // total_size

o = Order('0B', True)
order[0].append(o)
o = Order('0S', False)
order[1].append(o)

Order.core = core

done = False
#done = True
basis_per = 15
full_per = 25
tick_size = 100
#pp.pprint(core.get_pnl_vratio())
while done:
    time.sleep(2)
    pnl, vratio = core.get_pnl_vratio()
    
    for i in range(2):
        price = core.cur_price
        tick = 0
        ol = len(order[i])
        for j in range(ol): 
            o = order[i][j]
            if o.step == 0:
                o.qty = qty_size
                o.step = 1
                tick += (tick_size * (-1 if o.side else 1))
                tick_price = price + tick

                if vratio[i] < basis_per:
                    o.open_price = tick_price
                    if ol < 5:
                        order[i].append(str(ol) + ('B' if o.side else 'S'), o.side)
                elif vratio[i] < full_per:
                    o.side = not o.side
                    o.close = not o.close
                    open_price = round(float(core.my_pos[i+1]['entry_price'])) + (tick * (-1 if not o.side else 1))
                    o.open_price = open_price
                    o.step = 3

                        
            if o.step == 0:
                o.qty = qty_size
                o.step = 1
                tick += (tick_size * (-1 if o.side else 1))
                tick_price = price + tick

                if vratio[i] < basis_per:
                    o.open_price = tick_price
                                        
                elif vratio[i] < full_per:                         
                    open_price = round(float(core.my_pos[i+1]['entry_price'])) + tick
                    #print(open_price, price, Order.open_last_price[i])

                    if open_price < tick_price:
                        if not o.side:
                            open_price = tick_price
                    elif tick_price < open_price:
                        if o.side:
                            open_price = tick_price
                    
                    if pnl[i] < 0:
                        if o.side:
                            if Order.open_last_price[i] - tick_size < open_price:
                                open_price = Order.open_last_price[i] - tick_size
                        else:
                            if open_price < Order.open_last_price[i] + tick:
                                open_price = Order.open_last_price[i] + tick
                    
                    o.open_price = open_price
                
                else:
                    o.side = not o.side
                    o.close = not o.close
                    open_price = round(float(core.my_pos[i+1]['entry_price'])) + (tick * (-1 if not o.side else 1))
                    o.open_price = open_price
                    o.step = 3
                    
            elif o.step == 1:
                o.create_order()

            elif o.step == 2:
                Filled, _ = o.get_order_status(False)
                
                # if Filled:
                #     print("?????? ?????????.")    
                #     for ro in order[1-i]:
                #         if ro.step == 2:
                #             ro.change_order_price(ro.open_price - tick_size *(-1 if ro.side else 1))

            elif o.step == 3:
                o.create_order()
            elif o.step == 4:
                o.get_order_status(False)
                