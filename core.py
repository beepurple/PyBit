from pybit import HTTP
import configparser
import pprint as pp
import time

session = ''
symbol = ''
coin = ''
margin = 0.0
cur_price = 0.0

def init(_test, _symbol, _margin, access_type='1'):
    global session, margin 
    margin = _margin
    
    config = configparser.ConfigParser()

    config.read('myConfig.ini')

    host = 'BYBIT_'
    test_type = 'REAL'
    main_url = 'https://api.bybit.com'
    if _test:
        test_type = 'TEST'
        main_url = 'https://api-testnet.bybit.com'

    host += test_type + access_type
    api_key = config[host]['api_key']
    api_secret = config[host]['api_secret']
    session = HTTP(main_url, api_key=api_key, api_secret=api_secret)
    get_symbol_data(_symbol)

    print(host + " Server Connect Complete...")


def get_symbol_data(_symbol):
    global session, symbol, coin
    symbols = session.query_symbol()
    result = symbols['result']

    for sb in result:
        if sb['alias']  == _symbol:
            symbol = sb['name']
            if sb['quote_currency'] == 'USD':
                coin = sb['base_currency']
            elif sb['quote_currency'] == 'USDT':
                coin = sb['quote_currency']

            return sb

def get_balance():
    global session, symbol, coin
    result = session.get_wallet_balance(symbol=symbol)
    #pp.pprint(result['result'][coin])
    return float(result['result'][coin]['available_balance'])

def get_price():
    global session, symbol
    result = session.latest_information_for_symbol(symbol=symbol)
    return float(result['result'][0]['last_price'])

def get_total_qty():
    global coin
    price = get_price()
    balance = get_balance()
    cur_qty = 0.0

    if coin == 'USDT':
        cur_qty = round(balance / price, 3)
    else:
        cur_qty = round(price * balance, 2)
    
    return cur_qty

def get_order_status(_order_id=''):
    global session, symbol
    result = session.query_active_order(symbol=symbol, order_id=_order_id)

    if check_ret_code(result):
        return result['result']
    else:
        return ''

def get_my_position():
    global session, symbol
    result = session.my_position(symbol=symbol)['result']

    pos = [[],[]]

    for r in result:
        v = r['data']
        print("result = ", v['position_value'], v['entry_price'], v['side'], v['size'])

    return result

def create_order(_side, _qty, _price, _close):
    global session, symbol
    position_idx = 1
    if _close:
        if _side == 'Buy':
            position_idx = 2
    else:
        if _side == 'Sell':
            position_idx = 2
    
    result = session.place_active_order(position_idx=position_idx, symbol=symbol, side=_side, qty=_qty, price=_price, close_on_trigger=_close,
                                        order_type='Limit', time_in_force="PostOnly", reduce_only=False)

    if check_ret_code(result):
        return result['result']['order_id']
    else:
        return ''

def check_ret_code(result):
    if result['ret_code'] == 0:
        return True
    elif result['ret_code'] == 10006:
        print("접근이 많아 잠시 Sleep 합니다.")
        time.sleep(1)
        return False
    else:
        return False

def get_cur_time():
    now = time.localtime()
    return ("%04d/%02d/%02d %02d:%02d:%02d"
          % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))

def cancel_order(_order_id):
    global session, symbol
    return session.cancel_active_order(symbol=symbol, order_id=_order_id)

