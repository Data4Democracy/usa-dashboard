import requests
import numpy as np
import pandas as pd
import arrow

"""
small script to pull NYC crime data from https://data.cityofnewyork.us/Public-Safety/NYPD-Complaint-Data-Current-YTD/5uac-w243
data is saved as csv and grouped by number of incidents per crime per day of 2016
The above dataset has one datapoint per reported crime incident (the ofns_desc field)
"""
NYPD_COMPLAINTS_DATA_URL = "https://data.cityofnewyork.us/resource/7x9x-zpz6.csv?$limit=50000"

# read in csv to dataframe
crime_dataframe = pd.read_csv(NYPD_COMPLAINTS_DATA_URL)

# parse out the year, month and day of each crime
crime_dataframe['year'] = crime_dataframe['cmplnt_fr_dt'].map(lambda x: arrow.get(x).datetime.year)
crime_dataframe['month'] = crime_dataframe['cmplnt_fr_dt'].map(lambda x: arrow.get(x).datetime.month)
crime_dataframe['day'] = crime_dataframe['cmplnt_fr_dt'].map(lambda x: arrow.get(x).datetime.day)

# do a df groupby count to get the counts of each
crime_dataframe_grouped = crime_dataframe.groupby(['year', "month", "day", "ofns_desc"]).aggregate('count')
grouped = crime_dataframe_grouped.reset_index()
#because of the way count works, I don't actually need most of the columns, so the subset
grouped_subset = grouped.iloc[:, 0:5]
# make sure that the data time is actually 2016. There are a few erronous(?) entries with timestamps that aren't 2016... leave
# them out for now
grouped_subset = grouped_subset[grouped_subset['year'] == 2016]
# the count column is the last column in the df
current_count_header_name = grouped_subset.columns.values[len(grouped_subset.columns.values) -1]
final = grouped_subset.rename(columns = {current_count_header_name: 'count'})
# save to csv
final.to_csv('data/nyc-2016-crime.csv', index=False)
