import alpaca_trade_api as alpaca_trade_api
from source.logs import Logs

from os import getenv
from dotenv import load_dotenv
load_dotenv()


class AlpacaConnector():
    def __init__(self,logs_to_cloud):
        if getenv('USE_REAL_MONEY') == 'YES':
            self.url = 'https://api.alpaca.markets'
            self.__key_id = getenv('APCA_API_KEY_ID')
            self.__secret_key = getenv('APCA_API_SECRET_KEY')
        else:
            self.url = 'https://paper-api.alpaca.markets'
            self.__key_id = getenv('APCA_PAPER_KEY_ID')
            self.__secret_key = getenv('APCA_PAPER_SECRET_KEY')

        self.API = alpaca_trade_api.REST(
                    self.__key_id,
                    self.__secret_key,
                    base_url=self.url)

        self.polygon = self.API.polygon
        self.logs = Logs(name="alpaca trading", to_cloud=logs_to_cloud)
        self.positive_statuses = set([
            'new',
            'accepted',
            'pending_new',
            'accepted_for_bidding',
            'calculated',
            'partially_filled',
            'filled'])

    # TODO: ADD PRE and POST MARKET FUNCTIONALITY
    def get_market_status(self):
        clock = self.API.get_clock()
        return clock.is_open


    def get_balance(self):
        try:
            account = self.API.get_account()
            return float(account.buying_power)
        except:
            self.logs.warn(f'Not able to get account balance')
            return 0


    def get_last_price(self,ticker):
        try:
            ticker.replace('$','')
            quote = self.polygon.last_quote(ticker)
            self.logs.debug(f'Quote for {ticker}: {quote.bidprice}')
            return quote.bidprice
        except:
            self.logs.warn(f'Not able to retrieve last price for {ticker}')
            return -1

    def submit_market_buy(self,symbol,qty,limit):
        try:
            response = self.API.submit_order(
                symbol = symbol,
                qty = str(qty),
                side = 'buy',
                type = 'limit',
                time_in_force = 'day',
                limit_price=str(limit)
            )
            self.logs.info(f'Making a trade: Buying {qty} units of {symbol} at limit price of {limit}')
            return (response.status, response.id)
        except:
            self.logs.warn(f'Not able to place order for {symbol}')
            return (False, "-1")

    def submit_trailing_stop(self,symbol,qty,trail_percent):
        try:
            self.API.submit_order(
                symbol = symbol,
                qty = string(qty),
                side = 'sell',
                type = 'trailing_stop',
                time_in_force = 'gtc',
                trail_percent=trail_percent
                )
            self.logs.info('Trailing stop order status: response.status. Order ID: response.id')
            return (response.status, response.id)
        except:
            self.logs.warn(f'Not able to place trailing_stop sell order for {symbol}')
            return (False, "-1")

    def cancel_order(self, order_id):
        #In case the order doesn't fill correctly or the market closes or something
        try:
            self.API.cancel_order(order_id)

            if self.get_order_status(order_id) == 'canceled':
                return True
        except:
            pass

        self.logs.warn(f'Not able to cancel order with order_id: {order_id}')
        return False

    def get_order_status(self, order_id):
        return self.API.get_order(order_id).status



#NEED LOGIC TO CHECK IF THE MARKET ORDER EXECUTES. AND THEN AFTER TO EXECUTE THE SELL. If it doesnt execute and the price rises 5% above the limit, then cancel
#could also add a 30 min timer
