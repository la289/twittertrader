from pytest import fixture
from os import getenv

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir + '/source')
sys.path.append(parentdir)

from alpaca_connector import AlpacaConnector

USE_REAL_MONEY = False

@fixture
def alpaca():
    a = AlpacaConnector(False)
    a.url = 'https://paper-api.alpaca.markets'
    a.__key_id = getenv('APCA_PAPER_KEY_ID')
    a.__secret_key = getenv('APCA_PAPER_SECRET_KEY')
    return a

def test_paper_url(alpaca):
    return alpaca.url == 'https://paper-api.alpaca.markets'

def test_get_market_status(alpaca):
    assert not alpaca.get_market_status()

def test_get_balance(alpaca):
    assert 0 <= alpaca.get_balance()

def test_get_last_price(alpaca):
    assert alpaca.get_last_price("BLDP") > 0.0
    assert alpaca.get_last_price("GM") > 0.0
    assert alpaca.get_last_price("GOOG") > 0.0
    assert alpaca.get_last_price("SNAP") > 0
    #INVALID TICKERS
    # assert alpaca.get_last_price("") == -1
    # assert -1 == alpaca.get_last_price('PL')

def test_submit_market_buy_and_cancel_order(alpaca):
    (status, client_id) = alpaca.submit_market_buy('VFF', 1, 20)
    assert (False, -1) != (status, client_id)
    print(status, client_id)

    assert True == alpaca.cancel_order(client_id)

# def test_submit_market_buy_invalid(alpaca):
#     assert (False, -1) == alpaca.submit_market_buy('',1,20)

def test_cancel_order_nonexistent(alpaca):
    assert False == alpaca.cancel_order('061950fc-c35a-49a7-b99d-02a08300c732')

# def test_submit_trailing_stop_fail(alpaca):
#     (status, id) = alpaca.submit_trailing_stop('AAPL', 1,5)
#     assert status == False

# def test_submit_market_buy_and_trailing_stop(alpaca):
#     (status, client_id) = alpaca.submit_market_buy('AAPL', 1, 139)
#     assert (False, -1) != (status, client_id)

#     assert True == alpaca.submit_trailing_stop('AAPL',1,5)

# def test_get_order_status(alpaca):
#     assert 'canceled' == alpaca.get_order_status('061950fc-c35a-49a7-b99d-02a08300c732')
