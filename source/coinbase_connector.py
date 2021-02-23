from source.logs import Logs
from decimal import Decimal
import cbpro
import time

from os import getenv
from dotenv import load_dotenv
load_dotenv()


class CryptoTrader():
    def __init__(self, logs_to_cloud = False, use_real_money = (getenv('USE_REAL_MONEY') == 'YES')):
        self.logs = Logs(name="trading", to_cloud=logs_to_cloud)
        self.cb_public = cbpro.PublicClient()
        self.cb_stream = CBWebsocketClient
        if use_real_money:
            key = getenv('CB_PROD_KEY')
            b64secret = getenv('CB_PROD_B64SECRET')
            passphrase = getenv('CB_PROD_PASSPHRASE')
            self.coinbase = cbpro.AuthenticatedClient(key, b64secret, passphrase)
        else:
            key = getenv('CB_SANDBOX_KEY')
            b64secret = getenv('CB_SANDBOX_B64SECRET')
            passphrase = getenv('CB_SANDBOX_PASSPHRASE')
            self.coinbase = cbpro.AuthenticatedClient(key, b64secret, passphrase,
                                  api_url="https://api-public.sandbox.pro.coinbase.com")


    def get_balance(self, currency):
        accounts = self.coinbase.get_accounts()
        print(accounts)
        for account in accounts:
            if account['currency'] == currency:
                return float(account['balance'])

        return -1

    def get_last_price(self, currency):
        product_id = f'{currency}-USD'
        response = self.cb_public.get_product_ticker(product_id)
        if 'bid' in response:
            return float(response['bid'])

        return -1

    def submit_market_buy(self, currency, budget):
        product_id = f'{currency}-USD'
        response = self.coinbase.place_market_order(
                product_id=product_id,
                side='buy',
                funds= str(budget)
                )

        if 'status' in response:
            return response

        return False


    def submit_market_sell(self, currency, size):
        product_id = f'{currency}-USD'
        response = self.coinbase.place_market_order(
                product_id=product_id,
                side='sell',
                size= float(size)
                )
        self.logs.warn(f'Submitted market sell for {currency}. Response: {response}')

        return response

    # def cancel_order(self):
    #     pass

    def get_order_fill(self, order_id):
        response = list(self.coinbase.get_fills(order_id = order_id))
        # response = list(fills_gen)
        # print(response)
        if 'size' in response[0]:
            return response[0]
        else:
            return False

    def trailing_stop_order(self, currency, size, trail_percent,min_sell_price=0):
        wsClient = self.cb_stream(products=[f'{currency}-USD'], channels = ['ticker'])
        wsClient.start()
        self.logs.warn(f'Stream opened for {currency}')
        # print('size',size)
        # print('streaming')
        while ((wsClient.highest_price*(1-trail_percent/100) <= wsClient.last_price) or
               (wsClient.last_price <= min_sell_price) and
               wsClient.streaming):
            time.sleep(0.5)
            # print(wsClient.last_price, wsClient.highest_price)
            #TODO: Need some sort of error monitoring in case stream gets disconnected

        self.logs.warn(f'Trailing limit price found for {currency}. HWM: {wsClient.highest_price} | Trigger price: {wsClient.last_price}')
        response = self.submit_market_sell(currency, size)
        # print(response)
        wsClient.close()

        if 'status' in response:
            return response
        else:
            return False


        # This function needs to run in a seperate thread. might run for days?
        #opens stream for asset price
        # on message
        #if  price > highest_price, updated highest_price
        #elif price < highest_price*(1-trail_percent)
        #    execture market sell


class CBWebsocketClient(cbpro.WebsocketClient):
    def on_open(self):
        self.highest_price = 0
        self.last_price = 0
        self.streaming = True

    def on_message(self, msg):
        if 'price' in msg:
            self.last_price = float(msg['price'])
            if self.last_price > self.highest_price:
                self.highest_price = self.last_price

    def on_close(self):
        self.streaming = False
