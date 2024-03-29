from pytest import fixture
from threading import Timer
from time import sleep

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from source.twitter import Twitter
from source.twitter import TWITTER_CONSUMER_KEY
from source.twitter import TWITTER_CONSUMER_SECRET
from source.twitter import TWITTER_ACCESS_TOKEN
from source.twitter import TWITTER_ACCESS_TOKEN_SECRET
from source.twitter import INFLUENCER_USER_IDS
from source.analysis import Analysis


@fixture
def twitter():
    return Twitter(logs_to_cloud=False)

def analysis():
    return Analysis()

def test_environment_variables():
    print(INFLUENCER_USER_IDS)
    assert TWITTER_CONSUMER_KEY
    assert TWITTER_CONSUMER_SECRET
    assert TWITTER_ACCESS_TOKEN
    assert TWITTER_ACCESS_TOKEN_SECRET
    assert False


def callback(tweet):
    # TODO: Test the callback without relying on Trump tweets.
    assert tweet


def test_streaming(twitter):
    # Let the stream run for two seconds and run it again after a pause.
    Timer(2, twitter.stop_streaming).start()
    twitter.start_streaming(callback)
    sleep(2)
    Timer(2, twitter.stop_streaming).start()
    twitter.start_streaming(callback)

def test_post_tweet(twitter,analysis):
    assert twitter.test_tweet()

def test_make_tweet_text(twitter):
    assert twitter.make_tweet_text([{
        "name": "Boeing",
        "sentiment": -0.1,
        "ticker": "BA"}],
        "https://twitter.com/realDonaldTrump/status/806134244384899072") == (
        "Boeing \U0001f44e $BA\n"
        "https://twitter.com/realDonaldTrump/status/806134244384899072")
    assert twitter.make_tweet_text([{
        "name": "Ford",
        "sentiment": 0.3,
        "ticker": "F"}, {
        "name": "Fiat",
        "root": "Fiat Chrysler Automobiles",
        "sentiment": 0.3,
        "ticker": "FCAU"}],
        "https://twitter.com/realDonaldTrump/status/818461467766824961") == (
        "Ford \U0001f44d $F\n"
        "Fiat \U0001f44d $FCAU\n"
        "https://twitter.com/realDonaldTrump/status/818461467766824961")
    assert twitter.make_tweet_text([{
        "name": "Lockheed Martin",
        "sentiment": -0.1,
        "ticker": "LMT"}, {
        "name": "Boeing",
        "sentiment": 0.1,
        "ticker": "BA"}],
        "https://twitter.com/realDonaldTrump/status/812061677160202240") == (
        "Lockheed Martin \U0001f44e $LMT\n"
        "Boeing \U0001f44d $BA\n"
        "https://twitter.com/realDonaldTrump/status/812061677160202240")
    assert twitter.make_tweet_text([{
        "name": "General Motors",
        "sentiment": 0,
        "ticker": "GM"}],
        "https://twitter.com/realDonaldTrump/status/821697182235496450") == (
        "General Motors ¯\\_(\u30c4)_/¯ $GM\n"
        "https://twitter.com/realDonaldTrump/status/821697182235496450")
    assert twitter.make_tweet_text([{
        "ticker": "XOM",
        "name": "ExxonMobil",
        "sentiment": 0.5,
        "exchange": "New York Stock Exchange"}, {
        "root": "BlackRock",
        "ticker": "BLK",
        "name": "ExxonMobil",
        "sentiment": 0.5,
        "exchange": "New York Stock Exchange"}, {
        "root": "PNC Financial Services",
        "ticker": "PNC",
        "name": "ExxonMobil",
        "sentiment": 0.5,
        "exchange": "New York Stock Exchange"}, {
        "root": "State Street Corporation",
        "ticker": "STT",
        "name": "ExxonMobil",
        "sentiment": 0.5,
        "exchange": "New York Stock Exchange"}],
        "https://twitter.com/realDonaldTrump/status/838862131852369922") == (
        "ExxonMobil \U0001f44d $XOM $BLK $PNC $STT\n"
        "https://twitter.com/realDonaldTrump/status/838862131852369922")
    assert twitter.make_tweet_text([{
        "ticker": "GM",
        "name": "General Motors",
        "sentiment": 0.4,
        "exchange": "New York Stock Exchange"}, {
        "ticker": "WMT",
        "name": "Walmart",
        "sentiment": 0.4,
        "exchange": "New York Stock Exchange"}, {
        "root": "State Street Corporation",
        "ticker": "STT",
        "name": "Walmart",
        "sentiment": 0.4,
        "exchange": "New York Stock Exchange"}],
        "https://twitter.com/realDonaldTrump/status/821415698278875137") == (
        "General Motors \U0001f44d $GM\n"
        "Walmart \U0001f44d $WMT $STT\n"
        "https://twitter.com/realDonaldTrump/status/821415698278875137")
    assert twitter.make_tweet_text([{
        "ticker": chr(i - 32),
        "name": chr(i),
        "sentiment": 0} for i in range(97, 123)],
        "https://twitter.com/realDonaldTrump/status/0") == (
        "a ¯\\_(\u30c4)_/¯ $A\n"
        "b ¯\\_(\u30c4)_/¯ $B\n"
        "c ¯\\_(\u30c4)_/¯ $C\n"
        "d ¯\\_(\u30c4)_/¯ $D\n"
        "e ¯\\_(\u30c4)_/¯ $E\n"
        "f ¯\\_(\u30c4)_/¯ $F\n"
        "g ¯\\\u2026\n"
        "https://twitter.com/realDonaldTrump/status/0")


def test_get_sentiment_emoji(twitter):
    assert twitter.get_sentiment_emoji(0.5) == "\U0001f44d"
    assert twitter.get_sentiment_emoji(-0.5) == "\U0001f44e"
    assert twitter.get_sentiment_emoji(0) == "¯\\_(\u30c4)_/¯"
    assert twitter.get_sentiment_emoji(None) == "¯\\_(\u30c4)_/¯"


def test_get_tweet(twitter):
    tweet = twitter.get_tweet("1354885704615157761")
    print(tweet["full_text"])
    assert tweet["full_text"] == (
        "This is mostly what you need to know for $ETH "
        "https://t.co/Oc5uCi4zbu"
    )
    assert tweet["id_str"] == "1354885704615157761"
    assert tweet["user"]["id_str"] == "1091099554605395968"
    assert tweet["user"]["screen_name"] == "ShardiB2"
    assert tweet["created_at"] == "Thu Jan 28 20:14:59 +0000 2021"


def test_get_tweet_link(twitter):
    tweet = twitter.get_tweet("1354888469408051202")
    assert twitter.get_tweet_link(tweet) == (
        "https://twitter.com/ShardiB2/status/1354888469408051202")

from pprint import pprint


# def test_get_all_tweets(twitter):
#     pprint(twitter.get_all_tweets())

