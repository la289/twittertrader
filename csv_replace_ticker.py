import csv
import sys
from text_processor import text_processor


#read csv, and split on "," the line
csv_file = open('csv_test.csv', "r")

text_pro = text_processor()
x = open("output.csv","w")

#loop through the csv list
for row in csv_file:
    replaced_row = text_pro.replace_tickers_with_company_names(row)
    x.writelines(replaced_row)

x.close()
