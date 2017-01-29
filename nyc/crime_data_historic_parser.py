import requests
import numpy as np
import pandas as pd
import arrow
import config
app_token = config.app_token
def construct_data_url(year):
    url = "https://data.cityofnewyork.us/resource/9s4h-37hy.csv?$$app_token=" + app_token + "&$limit=18446744073&$where=CMPLNT_FR_DT>=%27" + str(year) + "-01-01%27%20AND%20CMPLNT_FR_DT<=%27" + str(year) + "-12-31%27"
    print(url)
    return url

def parse_data_from_url(url, year):
    crime_dataframe = pd.read_csv(url)
    crime_dataframe['year'] = crime_dataframe['cmplnt_fr_dt'].map(lambda x: arrow.get(x).datetime.year)
    crime_dataframe['month'] = crime_dataframe['cmplnt_fr_dt'].map(lambda x: arrow.get(x).datetime.month)
    crime_dataframe['day'] = crime_dataframe['cmplnt_fr_dt'].map(lambda x: arrow.get(x).datetime.day)
    crime_dataframe_grouped = crime_dataframe.groupby(['year', "month", "day", "ofns_desc"]).aggregate('count')
    grouped = crime_dataframe_grouped.reset_index()
    grouped_subset = grouped.iloc[:, 0:5]
    #double check that the return data is all in the year you want
    grouped_subset = grouped_subset[grouped_subset['year'] == year]
    current_count_header_name = grouped_subset.columns.values[len(grouped_subset.columns.values) -1]
    final = grouped_subset.rename(columns = {current_count_header_name: 'count'})
    final.to_csv('data/nyc-'+ str(year)+'-crime.csv', index=False)
    print('done' + str(year))

for x in range(2006, 2016):
    parse_data_from_url(construct_data_url(x), x)
