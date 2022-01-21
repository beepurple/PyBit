from pybit import HTTP
import configparser
import pprint as pp
import time


class Core:
    session = ''
    symbol = ''
    coin = ''
    margin = 0.0
    cur_price = 0.0

    my_pos = [[], [], []]

    @classmethod
    def __init__(cls, test, symbol, margin, access_type='1'):
        cls.margin = margin
    
        config = configparser.ConfigParser()

        config.read('myConfig.ini')

        host = 'BYBIT_'
        test_type = 'REAL'
        main_url = 'https://api.bybit.com'
        if test:
            test_type = 'TEST'
            main_url = 'https://api-testnet.bybit.com'

        host += test_type + access_type
        api_key = config[host]['api_key']
        api_secret = config[host]['api_secret']
        cls.session = HTTP(main_url, api_key=api_key, api_secret=api_secret)
        cls.get_symbol_data(symbol)

        print(host + " Server Connect Complete...")

    @classmethod
    def get_symbol_data(cls, symbol):
        symbols = cls.session.query_symbol()
        result = symbols['result']

        for sb in result:
            if sb['alias'] == symbol:
                cls.symbol = sb['name']
                if sb['quote_currency'] == 'USD':
                    cls.coin = sb['base_currency']
                elif sb['quote_currency'] == 'USDT':
                    cls.coin = sb['quote_currency']

                return sb

    @classmethod
    def get_balance(cls):        
        result = cls.session.get_wallet_balance(symbol=cls.symbol)
        cls.my_pos[0] = result['result'][cls.coin]
        
        return float(result['result'][cls.coin]['available_balance'])

    @classmethod
    def get_price(cls):
        result = cls.session.latest_information_for_symbol(symbol=cls.symbol)
        cls.cur_price = float(result['result'][0]['last_price']) 

        return cls.cur_price

    @classmethod
    def get_total_qty(cls):
        price = cls.get_price()
        balance = cls.get_balance()
        cur_qty = 0.0

        if cls.coin == 'USDT':
            cur_qty = round(balance / price, 3)
        else:
            cur_qty = round(price * balance, 2)
        
        return cur_qty

    @classmethod
    def get_order_status(cls, order_id=''):        
        result = cls.session.query_active_order(symbol=cls.symbol, order_id=order_id)

        if cls.check_ret_code(result):
            return result['result']
        else:
            return ''

    @classmethod
    def get_my_position(cls):
        
        # 오류 수정 필요
        result = cls.session.my_position(symbol=cls.symbol)['result']

        cls.get_balance()

        for r in result:
            v = r['data']
            cnt = 0
            if v['side'] == 'Buy':
                cnt = 1
            elif v['side'] == 'Sell':
                cnt = 2

            if cnt:
                cls.my_pos[cnt] = v
            #print("result = ", v['position_value'], v['entry_price'], v['side'], v['size'])

        return cls.my_pos

    @classmethod
    def create_order(cls, side, qty, price, close):        
        position_idx = 1
        if close:
            if side == 'Buy':
                position_idx = 2
        else:
            if side == 'Sell':
                position_idx = 2
        
        result = cls.session.place_active_order(position_idx=position_idx, symbol=cls.symbol, side=side, qty=qty, price=price, close_on_trigger=close,
                                                order_type='Limit', time_in_force="PostOnly", reduce_only=False)

        if cls.check_ret_code(result):
            return result['result']['order_id']
        else:
            return ''

    @classmethod
    def check_ret_code(cls, result):
        if result['ret_code'] == 0:
            return True
        elif result['ret_code'] == 10006:
            print("접근이 많아 잠시 Sleep 합니다.")
            time.sleep(1)
            return False
        else:
            return False

    @classmethod
    def get_cur_time(cls):
        now = time.localtime()
        return ("%04d/%02d/%02d %02d:%02d:%02d"
            % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))

    @classmethod
    def cancel_order(cls, order_id):        
        return cls.session.cancel_active_order(symbol=cls.symbol, order_id=order_id)

    @classmethod
    def get_pnl_vratio(cls):        
        cls.get_my_position()

        pnl = []
        vratio = []

        cls.get_price()
        entry_price = 0.0
        total_balance = cls.my_pos[0]['wallet_balance'] * cls.margin
        
        v1 = float(cls.my_pos[1]['position_value'])    
        v2 = float(cls.my_pos[2]['position_value'])

        volumn = v1 / total_balance * 100
        vratio.append(volumn)
        volumn = v2 / total_balance * 100
        vratio.append(volumn)
        volumn = (v1 + v2) / total_balance * 100
        vratio.append(volumn)

        entry_price = float(cls.my_pos[1]['entry_price'])
        pnl1 = ((cls.cur_price / entry_price * 100) - 100) * cls.margin
        entry_price = float(cls.my_pos[2]['entry_price'])
        pnl2 = ((cls.cur_price / entry_price * 100) - 100) * -cls.margin
        
        # print(v1, v2, pnl1, pnl2, total_balance, v1/total_balance * 100, v2/total_balance * 100)
        pnl3 = (pnl1 * v1 + pnl2 * v2) / (v1 + v2)
        
        pnl.append(pnl1)
        pnl.append(pnl2)
        pnl.append(pnl3)
        
        return pnl, vratio
