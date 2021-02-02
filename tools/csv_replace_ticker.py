import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir + '/source')
sys.path.append(parentdir)

import csv
from text_processor import TextProcessor


#read csv, and split on "," the line
csv_file = open('ShardiB2_2021-01-31 02:06:44.396227_tweets.csv', "r")

text_pro = text_processor()
x = open("no_links or tickers_ShardiB2_2021-01-31 02:06:44.396227_tweets.csv","w")

#loop through the csv list
for row in csv_file:
    replaced_row = text_pro.replace_tickers_with_company_names(row)
    #uncomment below to also remove links
    # index = replaced_row.find("https")
    # if index != -1:
    #     replaced_row = replaced_row[:index]
    x.writelines(replaced_row)

x.close()
