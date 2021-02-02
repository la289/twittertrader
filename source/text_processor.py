import requests
import json
import re
import assets.crypto_dict

class TextProcessor:
    """
    Find potential tickers in text and return text with
     the corresponding company names in place of the tickers
    """
    def replace_tickers_with_company_names(self, text):
        ## assert len(text) > 0
        if not text:
            return ""
        tickers = self.find_tickers(text)

        ticker_company_name_dict = self.convert_tickers_to_company_names(tickers)

        for ticker in tickers:
            text = text.replace(ticker, ticker_company_name_dict[ticker])

        return text

    """
    Parses input text and returns a set of potential ticker strings
    """
    def find_tickers(self, text):
        word_list = self.__split_text(text)
        tickers = set()

        for word in word_list:
            if  self.__is_ticker(word): ##move to is_ticker function
                tickers.add(word)
        return tickers

    def __is_ticker(self, ticker):
        return 1 < len(ticker) <= 5 and ticker[0] == '$' and ticker[1:].isalpha()

    ## making these private functions -> leads to errors with pytest
    def __split_text(self,text):
        if not text:
            return []
        delimiters = [" ", "\n", "!", "?", "%", "^", ".", "...", ";", ":", ">", "<", "+"]
        maxsplit=0
        regexPattern = '|'.join(map(re.escape, delimiters))
        return re.split(regexPattern, text, maxsplit)

    """
    return dict with key as ticker and value as string of company name
    """
    def convert_tickers_to_company_names(self, tickers):
        #return dict with key as ticker and value as string of company name
        ticker_company_name_dict = {}
        for ticker in tickers:
            if ticker[0] == '$':
                ticker_company_name_dict[ticker] = self.get_company_name(ticker)
        return ticker_company_name_dict

    """
    Query yahoo finance to return the company name of a ticker
    """
    def get_company_name(self, ticker):
        ##returns the ticker for each company name
        ##returns ticker if it cannot find a name

        ticker_alpha = ticker.strip('$')

        url = f'http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={ticker_alpha}&region=1&lang=en'
        response = requests.get(url)
        if response.status_code != 200:
            ## the right way is to raise an error here
            ## the function that calls get_company_name can catch the error
            ## and return ticker
            return ticker

        companies = response.json()['ResultSet']['Result']

        ## if not companies, raise
        ## have parent function handle the error

        for company in companies:
            if ticker_alpha in crypto_dict.crypto_dict:
                return crypto_dict.crypto_dict[ticker_alpha]
            elif company['symbol'] ==  ticker_alpha: #can different companies have the same tickers on different exchanges
                return company["name"]

        ## remove this, it will never get here because you raise beforehand.
        #if all else fails
        return ticker


class Error(Exception):
    """Base class for other exceptions"""
    pass

class ApiError(Error):
    pass
