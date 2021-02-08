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

from trading_alpaca import Trading


@fixture
def trading():
    t = Trading(logs_to_cloud=False)
    t.alpaca.url = 'https://paper-api.alpaca.markets'
    t.alpaca.__key_id = getenv('APCA_PAPER_KEY_ID')
    t.alpaca.__secret_key = getenv('APCA_PAPER_SECRET_KEY')
    return t

def test_get_strategy_blacklist(trading):
    assert trading.get_strategy({
        "exchange": "NASDAQ",
        "name": "Google",
        "sentiment": 0.4,
        "ticker": "GOOG"}, "open") == {
            "action": "hold",
            "exchange": "NASDAQ",
            "name": "Google",
            "reason": "blacklist",
            "sentiment": 0.4,
            "ticker": "GOOG"}

    assert trading.get_strategy({
        "exchange": "New York Stock Exchange",
        "name": "Ford",
        "sentiment": 0.3,
        "ticker": "F"}, "open") == {
            "action": "bull",
            "exchange": "New York Stock Exchange",
            "name": "Ford",
            "reason": "positive sentiment",
            "sentiment": 0.3,
            "ticker": "F"}


def test_get_strategy_market_status(trading):
    # assert trading.get_strategy({
    #     "exchange": "New York Stock Exchange",
    #     "name": "General Motors",
    #     "sentiment": 0.5,
    #     "ticker": "GM"}, "pre") == {
    #         "action": "bull",
    #         "exchange": "New York Stock Exchange",
    #         "name": "General Motors",
    #         "reason": "positive sentiment",
    #         "sentiment": 0.5,
    #         "ticker": "GM"}
    assert trading.get_strategy({
        "exchange": "New York Stock Exchange",
        "name": "General Motors",
        "sentiment": 0.5,
        "ticker": "GM"}, True) == {
            "action": "bull",
            "exchange": "New York Stock Exchange",
            "name": "General Motors",
            "reason": "positive sentiment",
            "sentiment": 0.5,
            "ticker": "GM"}
    # assert trading.get_strategy({
    #     "exchange": "New York Stock Exchange",
    #     "name": "General Motors",
    #     "sentiment": 0.5,
    #     "ticker": "GM"}, "after") == {
    #         "action": "hold",
    #         "exchange": "New York Stock Exchange",
    #         "name": "General Motors",
    #         "reason": "market closed",
    #         "sentiment": 0.5,
    #         "ticker": "GM"}
    assert trading.get_strategy({
        "exchange": "New York Stock Exchange",
        "name": "General Motors",
        "sentiment": 0.5,
        "ticker": "GM"}, False) == {
            "action": "hold",
            "exchange": "New York Stock Exchange",
            "name": "General Motors",
            "reason": "market closed",
            "sentiment": 0.5,
            "ticker": "GM"}


def test_get_strategy_sentiment(trading):
    assert trading.get_strategy({
        "exchange": "New York Stock Exchange",
        "name": "General Motors",
        "sentiment": 0,
        "ticker": "GM"}, "open") == {
            "action": "hold",
            "exchange": "New York Stock Exchange",
            "name": "General Motors",
            "reason": "neutral sentiment",
            "sentiment": 0,
            "ticker": "GM"}
    assert trading.get_strategy({
        "exchange": "New York Stock Exchange",
        "name": "Ford",
        "sentiment": 0.5,
        "ticker": "F"}, "open") == {
            "action": "bull",
            "exchange": "New York Stock Exchange",
            "name": "Ford",
            "reason": "positive sentiment",
            "sentiment": 0.5,
            "ticker": "F"}
    assert trading.get_strategy({
        "exchange": "New York Stock Exchange",
        "name": "Fiat",
        "root": "Fiat Chrysler Automobiles",
        "sentiment": -0.5,
        "ticker": "FCAU"}, "open") == {
            "action": "hold",
            "exchange": "New York Stock Exchange",
            "name": "Fiat",
            "reason": "negative sentiment",
            "root": "Fiat Chrysler Automobiles",
            "sentiment": -0.5,
            "ticker": "FCAU"}


def test_get_budget(trading):
    assert trading.get_budget(25250.0, 1) == 30
    assert trading.get_budget(11000.0, 2) == 0
    assert trading.get_budget(28000.0, 3) == 30
    assert trading.get_budget(28000.0, 0) == 0.0

def test_get_buy_limit(trading):
    assert trading.get_buy_limit(34.84) == 35.89


def test_get_sell_limit(trading):
    assert trading.get_sell_limit(34.84) == 33.79


def test_get_quantity(trading):
    quantity, price = trading.get_quantity("F", 10000.0)
    assert quantity > 0
    assert price > 0


# def test_bull(trading):
    # TODO: Find a way to test while the markets are closed and how to test
    #       sell short orders without holding the stock.
    # assert trading.bull("F", 10000.0)


# def test_bear(trading):
    # TODO: Find a way to test while the markets are closed and how to test
    #       sell short orders without holding the stock.
    # assert trading.bear("F", 10000.0)





def test_make_trades_fail(trading):
    assert not trading.make_trades([{
        "exchange": "New York Stock Exchange",
        "name": "Boeing",
        "sentiment": 0,
        "ticker": "BA"}])
