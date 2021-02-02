from ast import literal_eval
from google.cloud import language
from twitter import Twitter
from pprint import pprint


import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir + '/source')
sys.path.append(parentdir)

a = Twitter(False)

pprint(a.get_all_tweets())
