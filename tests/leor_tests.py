import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir + '/source')
sys.path.append(parentdir)

from ast import literal_eval
from google.cloud import language
from twitter import Twitter
from pprint import pprint
from analysis import Analysis


a = Analysis(False)

print(a.get_monkey_sentiment('jake sucks'))

