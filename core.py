from pybit import HTTP
import configparser
import pprint as pp
import time

session = ''
symbol = ''
coin = ''

def init(_test, _symbol, access_type='2'):
    global session
    symbol = _symbol
    testnet = _test

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
    return float(result['result'][coin]['available_balance'])

def get_price():
    global session, symbol
    result = session.latest_information_for_symbol(symbol=symbol)
    return float(result['result'][0]['last_price'])

def create_order(_side, _qty, _price, _close):
    global session, symbol
    position_idx = 1
    if _side == 'Sell':
        position_idx = 2
    
    result = session.place_active_order(position_idx=position_idx, symbol=symbol, side=_side, qty=_qty, price=_price, #close_on_trigger=_close,
                                        order_type='Limit', time_in_force="PostOnly")

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