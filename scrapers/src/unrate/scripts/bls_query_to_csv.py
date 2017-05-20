"""
Usage: 
    $ python3 bls_query_to_csv.py LNS14000000 --key (authentication key) --start
    yyyy --end yyyy
"""
import argparse
import requests
import json
from datetime import datetime as dt

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
        "fetch", 
        help="fetch data sets specified at the command line by series IDs from BLS",
        nargs='+',
        type=str
        )

parser.add_argument(
        "--delimiter", "-d",
        help="specify csv delimiter",
        type=str,
        default=',',
        )

args = parser.parse_args()

# For more info on this check out https://www.bls.gov/developers/api_python.htm
headers = {'Content-type': 'application/json'}
data = json.dumps({'seriesid': args.fetch, 'startyear': args.start, 'endyear':
    args.end, 'registrationkey': args.key})

p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/',
        data=data, headers=headers)

json_data = json.loads(p.text)

for (i, series) in enumerate(json_data['Results']['series']):
    # I'm assuming that the header for the first entry in the series is the
    # header for every entry in the series. I don't know if that is bad.
    header = list(series['data'][0].keys())
    with open('../data/{}.csv'.format(series['seriesID']), 'w+') as f:
        f.write(args.delimiter.join(header + ['\n']))
        for item in series['data']:
            f.write(args.delimiter.join([str(item[column]) for column in header] + ['\n']))

        
            


