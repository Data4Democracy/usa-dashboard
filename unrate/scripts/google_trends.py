"""
Usage:
    $ python3 google_trends google_username google_password
"""
from pytrends.request import TrendReq
from datetime import datetime as dt
import pandas as pd
import argparse

# Argument parsing
parser = argparse.ArgumentParser()

parser.add_argument(
        "user",
        help="Google account user name",
        type=str
        )

parser.add_argument(
        "pswd",
        help="Google account password",
        type=str
        )

args = parser.parse_args()

# credentials
username = args.user
password = args.pswd

language = 'en-US'
timezone = 360

query_terms = ['jobs']

# time span for search
# times = 'YYYY-MM-DD YYYY-MM-DD', where the first substring is the start 
# date and the second substring is the end date
start = str(dt(2016, 1, 1).date())
end = str(dt.today().date())
times = "{} {}".format(start, end)

# geographic details
location='US'

# establish connection
query = TrendReq(username, 
        password, 
        hl=language, 
        tz=timezone, 
        custom_useragent=None)

# query setup
query.build_payload(query_terms, 
        cat=0, 
        timeframe=times,
        geo='US', 
        gprop='')

# request to pandas table
data = query.interest_over_time()

print(data.tail())

data.to_csv('../data/google/{}.{}.csv'.format('_'.join(query_terms), times))
