# twitterTrader

This bot watches an Influencer's twitter and waits for the influencer to mention
any publicly traded companies. When he does, it
uses sentiment analysis to determine whether his opinions are positive or
negative toward those companies. The bot then automatically executes trades on
the relevant stocks according to the expected market reaction. It also tweets
out a summary of its findings in real time.


The code is written in Python and is meant to run on a
[Google Compute Engine](https://cloud.google.com/compute/) instance. It uses the
[Twitter Streaming APIs](https://dev.twitter.com/streaming/overview) to get
notified whenever influencers tweet. The entity detection and sentiment analysis is
done using Google's
[Cloud Natural Language API](https://cloud.google.com/natural-language/) and the
[Wikidata Query Service](https://query.wikidata.org/) provides the company data.
The [Alpaca API](https://alpaca.markets/) and [Coinbase API](https://docs.pro.coinbase.com/) do the stock trading.

The [`main`](main.py) module defines a callback where incoming tweets are
handled and starts streaming the influencer's feed:

```python
def twitter_callback(tweet):
    companies = analysis.find_companies(tweet)
    if companies:
        trading_alpaca.make_trades(companies)
        twitter.tweet(companies, tweet)

if __name__ == "__main__":
    twitter.start_streaming(twitter_callback)
```

The core algorithms are implemented in the [`analysis`](analysis.py) and [`trading`](trading_alpaca.py) modules. The former finds mentions of companies or assets in the text of the tweet, figures out what their ticker symbol is, and assigns a sentiment score to them. The latter chooses a trading strategy, which is either buy now or hold. After a stock buy is executed, a trailing limit stop order is placed. The limit percent is pulled from the `.env` file. When trading crypto, the bot opens a stream and tracks the price to manually perform a trailing limit stop when the price trails by a limit percent (also pulled from `.env`).  The [`twitter`](twitter.py) module deals with streaming tweets and tweeting out the summary.

Follow these steps to run the code yourself:

### 1. Create VM instance

Check out the [quickstart](https://cloud.google.com/compute/docs/quickstart-linux)
to create a Cloud Platform project and a Linux VM instance with Compute Engine,
then SSH into it for the steps below. Pick a predefined
[machine type](https://cloud.google.com/compute/docs/machine-types) matching
your preferred price and performance.


### 2. Set up auth

The authentication keys for the different APIs are read from shell environment
variables. Each service has different steps to obtain them.

#### Twitter

Log in to your [Twitter](https://twitter.com/) account and
[create a new application](https://apps.twitter.com/app/new). Under the *Keys
and Access Tokens* tab for [your app](https://apps.twitter.com/) you'll find
the *Consumer Key* and *Consumer Secret*. Add both to the `.env` file:

```bash
TWITTER_CONSUMER_KEY="<YOUR_CONSUMER_KEY>"
TWITTER_CONSUMER_SECRET="<YOUR_CONSUMER_SECRET>"
```

If you want the tweets to come from the same account that owns the application,
simply use the *Access Token* and *Access Token Secret* on the same page. If
you want to tweet from a different account, follow the
[steps to obtain an access token](https://dev.twitter.com/oauth/overview). Then
add both to the `.env` file::

```bash
TWITTER_ACCESS_TOKEN="<YOUR_ACCESS_TOKEN>"
TWITTER_ACCESS_TOKEN_SECRET="<YOUR_ACCESS_TOKEN_SECRET>"
```

#### Google

Follow the
[Google Application Default Credentials instructions](https://developers.google.com/identity/protocols/application-default-credentials#howtheywork)
to create, download, and export a service account key.

```bash
GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials-file.json"
```

You also need to [enable the Cloud Natural Language API](https://cloud.google.com/natural-language/docs/getting-started#set_up_your_project)
for your Google Cloud Platform project.

#### Alpaca

### Coinbase Pro

### 3. Install dependencies

There are a few library dependencies, which you can install using
[pip](https://pip.pypa.io/en/stable/quickstart/):

```shell
$ pip install -r requirements.txt
```

### 4. Run the tests

Verify that everything is working as intended by running the tests with
[pytest](https://doc.pytest.org/en/latest/getting-started.html) using this
command:

```shell
$ pytest *.py -vv
```

### 5. Run the benchmark

WARNING: THE BENCHMARK IS SUPER OUTDATED, AS I HAVE NOT HAD TIME TO UPDATE IT FOR THE LATEST TRADING STRATEGIES.
The [benchmark report](benchmark.md) shows how the current implementation of the
analysis and trading algorithms would have performed against historical data.
You can run it again to benchmark any changes you may have made. You'll need a [Polygon](https://polygon.io) account and add the API key to the `.env` file:
```bash
POLYGON_API_KEY="<YOUR_POLYGON_API_KEY>"
```

```shell
$ python benchmark.py > benchmark.md
```

### 6. Start the bot

Enable real orders that use your by adding the following to the `.env` file:

```bash
USE_REAL_MONEY=YES
```

Have the code start running in the background with this command:

```shell
$ nohup python main.py &
```
