import requests
import json
import re
import crypto_dict

class text_processor:
    def __init__(self):
        self.crypto_dict = crypto_dict.crypto_dict

    def find_tickers(self, text):
        #parse input string and make set of potential ticker strings
        word_list = self.split_text(text)
        tickers = set()

        if not word_list:
            return tickers

        tickers = set()
        for word in word_list:
            if  1 < len(word) <= 5 and word[0] == '$' and word[1:].isalpha():
                tickers.add(word)
        return tickers

    def split_text(self,text):
        if not text:
            return
        delimiters = [" ", "\n", "!", "?", "%", "^", ".", "...", ";", ":", ">", "<", "+"]
        maxsplit=0
        regexPattern = '|'.join(map(re.escape, delimiters))
        return re.split(regexPattern, text, maxsplit)


    def convert_tickers_to_company_names(self, tickers):
        #return dict with key as ticker and value as string of company name
        ticker_company_name_dict = {}
        for ticker in tickers:
            if ticker[0] == '$':
                ticker_company_name_dict[ticker] = self.get_company_name(ticker)
        return ticker_company_name_dict




    def get_company_name(self, ticker):
        #returns the ticker for each company name
        #returns ticker if it cannot find a name
        ticker_alpha = ticker[1:]

        response = requests.get(f'http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={ticker_alpha}&region=1&lang=en')
        if response.status_code != 200:
            return ticker

        companies = response.json()['ResultSet']['Result']

        for company in companies:
            if ticker_alpha in self.crypto_dict:
                return self.crypto_dict[ticker_alpha]
            elif company['symbol'] ==  ticker_alpha: #can different companies have the same tickers on different exchanges
                return company["name"]

        #if all else fails
        return ticker



    def replace_tickers_with_company_names(self, text):
        #find potential tickers in string and replace them with company name
        if not text:
            return ""
        tickers = self.find_tickers(text)

        ticker_company_name_dict = self.convert_tickers_to_company_names(tickers)

        # words = self.split_text(text)
        # for i in range(len(words)):
        #     if words[i] in tickers:
        #         words[i] = ticker_company_name_dict[words[i]]

        for ticker in tickers:
            text = text.replace(ticker, ticker_company_name_dict[ticker])

        return text
