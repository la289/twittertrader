from datetime import datetime
from pytest import fixture
from pytz import utc
from os import getenv
import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir + '/source')
sys.path.append(parentdir)

from trading_alpaca_crypto import Trading


@fixture
def trading():
    t = Trading(logs_to_cloud=False)
    t.alpaca.url = 'https://paper-api.alpaca.markets'
    t.alpaca.__key_id = getenv('APCA_PAPER_KEY_ID')
    t.alpaca.__secret_key = getenv('APCA_PAPER_SECRET_KEY')
    t.trail_percent = .005
    return t



# def test_crypto_bull(trading):
#     assert True == trading.crypto_bull('BTC',100)

def test_get_budget(trading):
    assert trading.get_crypto_budget(25250.0, 1) == 50
    assert trading.get_crypto_budget(11000.0, 2) == 50
    assert trading.get_crypto_budget(11000.0, 3) == 50
    assert trading.get_crypto_budget(11000.0, 0) == 0
    assert trading.get_stock_budget(25250.0, 1) == 50
    assert trading.get_stock_budget(11000.0, 2) == 0
    assert trading.get_stock_budget(11000.0, 3) == 0
    assert trading.get_stock_budget(11000.0, 0) == 0
