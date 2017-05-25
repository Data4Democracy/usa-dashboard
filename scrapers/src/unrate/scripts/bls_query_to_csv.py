"""
Usage: 
    $ python3 bls_query_to_csv.py LNS14000000 --key (authentication key) --start
    yyyy --end yyyy
"""
import argparse
from datetime import datetime as dt
from bls import api

parser = argparse.ArgumentParser()

# BLS will give you a free authentication key which lets you perform up to 500
# requests per day.
parser.add_argument(
        "--key", '-k',
        help="authenticate the BLS API request",
        type=str
        )

parser.add_argument(
        '--start', '-s',
        help="specify the starting year for the series",
        type=str,
        default='2012', # no good reason why this is 2012
        )


parser.add_argument(
        '--end', '-e',
        help="specify the ending year for the series",
        type=str,
        default=str(dt.today().year),
        )

parser.add_argument(
        "series",
        help=("fetch data sets specified at the command line by series IDs "
              "from BLS"),
        nargs='+',
        type=str
        )

args = parser.parse_args()

data = api.get_series(series=args.series,
                      startyear=args.start,
                      endyear=args.end,
                      key=args.key)

data.to_csv('../data/national/{}.{} {}.csv'.format(','.join(args.series),
                                                   args.start,
                                                   args.end),
            header=True,
            index_label='date')
        
            


