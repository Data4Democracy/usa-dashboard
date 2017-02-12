import requests
import numpy as np
import pandas as pd
import arrow

'''
taking format from nyc historical scraper
'''

def construct_data_url(year):
    url = "https://data.seattle.gov/resource/hapq-73pk.csv?$limit=18446744073&$where=report_date>=%27" + str(year) + "-01-01%27%20AND%20report_date<=%27" + str(year) + "-12-31%27"
    print(url)
    return url

def parse_data_from_url(url, year):
    crime_dataframe = pd.read_csv(url)
    crime_dataframe['year'] = crime_dataframe['report_date'].map(lambda x: arrow.get(x).datetime.year)
    crime_dataframe['month'] = crime_dataframe['report_date'].map(lambda x: arrow.get(x).datetime.month)
    crime_dataframe['day'] = crime_dataframe['report_date'].map(lambda x: arrow.get(x).datetime.day)
    crime_dataframe_grouped = crime_dataframe.groupby(['year', "month", "day", "crime_type"]).agg({'stat_value': np.sum})
    grouped = crime_dataframe_grouped.reset_index()
    grouped_subset = grouped.iloc[:, 0:5]
    #double check that the return data is all in the year you want
    grouped_subset = grouped_subset[grouped_subset['year'] == year]
    current_count_header_name = grouped_subset.columns.values[len(grouped_subset.columns.values) -1]
    final = grouped_subset.rename(columns = {current_count_header_name: 'count'})
    final.to_csv('data/sea-'+ str(year)+'-crime.csv', index=False)
    print('done' + str(year))

for x in range(2008, 2015):
    parse_data_from_url(construct_data_url(x), x)