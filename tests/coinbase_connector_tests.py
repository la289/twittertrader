from pytest import fixture
from os import getenv

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir + '/source')
sys.path.append(parentdir)

from coinbase_connector import CryptoTrader

USE_REAL_MONEY = 'YES'

@fixture
def crypto_trader():
    return CryptoTrader(False, True)

def test_get_accounts(crypto_trader):
    assert crypto_trader.coinbase.get_accounts()

def test_get_balance(crypto_trader):
    assert -1 == crypto_trader.get_balance('USD')

def test_get_last_price(crypto_trader):
    assert 1000 <= crypto_trader.get_last_price('ETH')

# def test_submit_market_buy(crypto_trader):
#     assert 'pending' == crypto_trader.submit_market_buy('BTC',100)

# def test_trailing_stop_order(crypto_trader):
#     assert 'pending' == crypto_trader.trailing_stop_order("BTC",0.11,.005)

