"""
Usage: python google_trends.py [-h] [--start START] [--end END]
                        user pswd terms [terms ...]
"""
from pytrends.request import TrendReq
from datetime import datetime as dt
import argparse

# Argument parsing
parser = argparse.ArgumentParser()

parser.add_argument(
    "user",
    help="Google account user name",
    type=str,
    nargs=1
)

parser.add_argument(
    "password",
    help="Google account password",
    type=str,
    nargs=1
)

parser.add_argument(
    "terms",
    help="Desired search terms to be queried",
    type=str,
    nargs='+'
)

parser.add_argument(
    "--start",
    help="Start date, formatted YYYY-MM-DD",
    type=str,
    default=str(dt(dt.today().year - 1, 1, 1).date())
)

parser.add_argument(
    "--end",
    help="End date, formatted YYYY-MM-DD",
    type=str,
    default=str(dt.today().date())
)

args = parser.parse_args()

# credentials
username = args.user
password = args.password

language = 'en-US'
timezone = 360

query_terms = args.terms

# time span for search
# times = 'YYYY-MM-DD YYYY-MM-DD', where the first substring is the start 
# date and the second substring is the end date
times = " ".join([args.start, args.end])

# geographic details
location = 'US'

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
