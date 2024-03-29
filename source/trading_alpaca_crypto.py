from os import getenv
import time
from source.alpaca_connector import AlpacaConnector
from assets.crypto_dict import crypto_dict
from threading import Thread
from threading import Timer

from source.logs import Logs
from source.coinbase_connector import CryptoTrader
from dotenv import load_dotenv
load_dotenv()


# Blacklsited stock ticker symbols, e.g. to avoid insider trading.
TICKER_BLACKLIST = ["GOOG", "GOOGL","GME","SPCE","AMC","GME","ETH","BTC","DOGE"]


class Trading:
    """A helper for making stock trades."""

    def __init__(self, logs_to_cloud):
        self.logs = Logs(name="trading", to_cloud=logs_to_cloud)
        self.alpaca = AlpacaConnector(logs_to_cloud)
        self.trail_percent = float(getenv('TRAIL_PERCENT'))
        self.limit_percent = float(getenv('LIMIT_PERCENT')) # The fraction of the stock price at which to set order limits.
        self.stock_cash_hold = float(getenv('STOCK_CASH_HOLD')) # The amount of cash in dollars to hold from being spent.
        self.max_stock_position = float(getenv('MAX_STOCK_POSITION')) # Max position to take for each trade
        self.crypto_cash_hold = float(getenv('CRYPTO_CASH_HOLD'))
        self.max_crypto_position = float(getenv('MAX_CRYPTO_POSITION'))
        self.crypto = CryptoTrader(logs_to_cloud)



    def make_trades(self, companies):
        """Executes trades for the specified companies based on sentiment."""
        self.logs.info(f'Trading received this company list: {companies}')
        # Determine whether the markets are open.
        is_market_open = self.alpaca.get_market_status()
        # if not is_market_open:
        #     self.logs.error("Not trading while market is closed")
        #     return False

        # Filter for any strategies resulting in trades.
        actionable_strategies = []
        for company in companies:
            strategy = self.get_strategy(company, is_market_open)
            if strategy["action"] != "hold":
                actionable_strategies.append(strategy)
            else:
                self.logs.warn("Dropping strategy: %s" % strategy)

        if not actionable_strategies:
            self.logs.warn("No actionable strategies for trading.")
            return False

        crypto_strategies = []
        stock_strategies = []
        for strategy in actionable_strategies:
            if strategy['ticker'] in crypto_dict:
                crypto_strategies.append(strategy)
            else:
                stock_strategies.append(strategy)
        self.logs.info(f'Passing on crypto strategies: {crypto_strategies} and stock strategies {stock_strategies} from combined strategies {actionable_strategies}')


        stock_execution = self.execute_stock_strategies(stock_strategies)
        crypto_execution = self.execute_crypto_strategies(crypto_strategies)
        return stock_execution and crypto_execution



    def execute_stock_strategies(self, stock_strategies):
        ####TODO seperate teh below into a stock helper function. Make a similar but different crypto trading function
        # Handle trades for each strategy.
        # Calculate the budget per strategy.
        balance = self.alpaca.get_balance()
        budget = self.get_stock_budget(balance, len(stock_strategies))

        if not budget:
            self.logs.warn("No budget for trading: %s %s %s" %
                           (budget, balance, stock_strategies))
            return False

        self.logs.debug("Using budget: %s x $%s" %
                        (len(stock_strategies), budget))


        success = True
        for strategy in stock_strategies:
            ticker = strategy["ticker"]
            action = strategy["action"]

            # Execute the strategy. ##BEEP
            if action == "bull":
                self.logs.info("Bull: %s %s" % (ticker, budget))
                success = success and self.bull(ticker, budget)
            elif action == "bear":
                self.logs.info("Bear: %s %s" % (ticker, budget))
                success = success and self.bear(ticker, budget)
            else:
                self.logs.error("Unknown strategy: %s" % strategy)

        return success

    def execute_crypto_strategies(self, crypto_strategies):
        ####TODO seperate teh below into a stock helper function. Make a similar but different crypto trading function
        # Handle trades for each strategy.
        # Calculate the budget per strategy.
        balance = self.crypto.get_balance('USD')
        budget = self.get_crypto_budget(balance, len(crypto_strategies))

        if not budget:
            self.logs.warn("No budget for trading: %s %s %s" %
                           (budget, balance, crypto_strategies))
            return False

        self.logs.debug("Using budget: %s x $%s" %
                        (len(crypto_strategies), budget))


        success = True
        for strategy in crypto_strategies:
            ticker = strategy["ticker"]
            action = strategy["action"]

            # Execute the strategy. ##BEEP
            if action == "bull":
                self.logs.info("Bull: %s %s" % (ticker, budget))
                success = success and self.crypto_bull(ticker, budget)
            elif action == "bear":
                self.logs.info("Bear: %s %s" % (ticker, budget))
                success = success and self.bear(ticker, budget)
            else:
                self.logs.error("Unknown strategy: %s" % strategy)

        return success


    def get_strategy(self, company, is_market_open):
        """Determines the strategy for trading a company based on sentiment and
        market status.
        """

        ticker = company["ticker"]
        sentiment = company["sentiment"]

        strategy = {}
        strategy["name"] = company["name"]
        if "root" in company:
            strategy["root"] = company["root"]
        strategy["sentiment"] = company["sentiment"]
        strategy["ticker"] = ticker
        if "exchange" in company:
            strategy["exchange"] = company["exchange"]

        # Don't do anything with blacklisted stocks.
        if ticker in TICKER_BLACKLIST:
            strategy["action"] = "hold"
            strategy["reason"] = "blacklist"
            return strategy

        # TODO: Figure out some strategy for the markets closed case.
        # Don't trade unless the markets are open or are about to open.
        if not is_market_open and ticker not in crypto_dict:
            strategy["action"] = "hold"
            strategy["reason"] = "market closed"
            return strategy

        # Can't trade without sentiment.
        if sentiment == 0:
            strategy["action"] = "hold"
            strategy["reason"] = "neutral sentiment"
            return strategy

        # Determine bull or bear based on sentiment direction.
        if sentiment > 0:
            strategy["action"] = "bull"
            strategy["reason"] = "positive sentiment"
            return strategy
        else:  # sentiment < 0
            strategy["action"] = "hold" #typically "bear", but i dont want to short anything
            strategy["reason"] = "negative sentiment"
            return strategy

    def get_stock_budget(self, balance, num_strategies):
        """Calculates the budget per company based on the available balance."""

        if num_strategies <= 0:
            self.logs.warn("No stock budget without strategies.")
            return 0.0
        return round(min(self.max_stock_position, max(0.0, balance - self.stock_cash_hold) / num_strategies), 2)

    def get_crypto_budget(self, balance, num_strategies):
        """Calculates the budget per asset based on the available balance."""

        if num_strategies <= 0:
            self.logs.warn("No crypto budget without strategies.")
            return 0.0
        return round(min(self.max_crypto_position, max(0.0, balance - self.crypto_cash_hold) / num_strategies), 2)

    def get_buy_limit(self, price):
        """Calculates the limit price for a buy (or cover) order."""

        return round((1 + self.limit_percent/100) * price, 2)

    def get_sell_limit(self, price):
        """Calculates the limit price for a sell (or short) order."""

        return round((1 - self.limit_percent/100) * price, 2)


    def get_quantity(self, ticker, budget):
        """Calculates the quantity of a stock based on the current market price
        and a maximum budget.
        """

        # Calculate the quantity based on the current price and the budget.
        price = self.alpaca.get_last_price(ticker)

        if price == -1:
            self.logs.error("Failed to determine price for: %s" % ticker)
            return (None, None)

        # Use maximum possible quantity within the budget.
        quantity = int(budget // price)
        self.logs.debug("Determined quantity %s for %s at $%s within $%s." %
                        (quantity, ticker, price, budget))

        return (quantity, price)

    def bull(self, ticker, budget):
        """Executes the bullish strategy on the specified stock within the
        specified budget: Buy now at market rate and sell at market rate at
        close.
        """

        # Calculate the quantity.
        quantity, price = self.get_quantity(ticker, budget)
        if not quantity:
            self.logs.warn(f'Cannot trade quantity = {quantity}')
            return False

        # Buy the stock now.
        self.logs.info(f'Trying to buy {quantity} units of {ticker}')
        buy_limit = self.get_buy_limit(price)
        buy_status, buy_order_id = self.alpaca.submit_market_buy(ticker, quantity, buy_limit)
        if buy_status not in self.alpaca.positive_statuses:
            return False

        # TODO: Do this properly by checking the order status API and using
        #       retries with exponential backoff.
        #wait for stock order to be filled
        timeout = time.time() + 60*10
        check_interval = 15
        while self.alpaca.get_order_status(buy_order_id) != 'filled' and time.time() > timeout:
            time.sleep(check_interval) #order not filled for 10 minutes
            check_interval *= 1.1

        if self.alpaca.get_order_status(buy_order_id) != 'filled':
            self.logs.warn(f'Not able to fill buy for {ticker}. Cancelling order')
            self.alpaca.cancel_order(buy_order_id)
            return False

        self.logs.warn(f'Trying to place trailing stop sell order for {ticker}')
        #Create trailing_stop_order
        sell_order_status, sell_order_id = self.alpaca.submit_trailing_stop(ticker, quantity, self.trail_percent)
        if sell_order_status == False:
            self.logs.error(f'Not able to place trailing_stop sell order for {ticker}. Order status: {sell_order_status} | Order ID: {sell_order_id}')

        return True


    def crypto_bull(self, ticker, budget):
        """Executes the bullish strategy on the specified stock within the
        specified budget: Buy now at market rate and sell at market rate at
        close.
        """

        # Buy the asset now.
        response = self.crypto.submit_market_buy(ticker,budget)
        if not response:
            self.logs.warn(f'Bad response returned for {ticker} order: {response}. Returning')
            return False

        if 'id' not in response:
            return False

        while True:
            response = self.crypto.get_order_fill(response['id'])
            if response['size'] != '0':
                size = response['size']
                buy_price = response['price']
                break

        self.logs.info(f'Opening thread to place trailing stop sell order for {ticker}')
        trailing_stop_thread = Thread(target=self.crypto.trailing_stop_order, args=(ticker, size, self.trail_percent,buy_price))
        trailing_stop_thread.start()

        return True


    def bear(self, ticker, budget):
        return False
        """Executes the bearish strategy on the specified stock within the
        specified budget: Sell short at market rate and buy to cover at market
        rate at close.
        """
        """
        # Calculate the quantity.
        quantity, price = self.get_quantity(ticker, budget)
        if not quantity:
            self.logs.warn("Not trading without quantity.")
            return False

        # Short the stock now.
        short_limit = self.get_sell_limit(price)
        short_fixml = self.fixml_short_now(ticker, quantity, short_limit)
        if not self.make_order_request(short_fixml):
            return False

        # Cover the short at close.
        cover_limit = self.get_buy_limit(price)
        cover_fixml = self.fixml_cover_eod(ticker, quantity, cover_limit)
        # TODO: Do this properly by checking the order status API and using
        #       retries with exponential backoff.
        # Wait until the previous order has been executed.
        Timer(ORDER_DELAY_S, self.make_order_request, [cover_fixml]).start()

        return True
        """
