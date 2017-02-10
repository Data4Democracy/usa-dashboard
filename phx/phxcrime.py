import numpy as np
import pandas as pd
import arrow
import datetime
import urllib
 
#setup variables for year links
rawlink = "https://www.phoenix.gov/OpenDataFiles/Crime%20Stats.csv"
crime_dataframe = pd.read_csv(rawlink)

#clean-up data: Replace blank with nan
crime_dataframe = crime_dataframe.applymap(lambda x: np.nan if str(x) and str(x).isspace() else str(x))
#Replace nan with Jan 1, 1900 (Probably don't need the nan step?)
crime_dataframe = crime_dataframe.replace('nan','01/01/1900  00:00', regex=True)

crime_dataframe['year'] = crime_dataframe['OCCURRED ON'].map(lambda x: arrow.get(str(x), 'MM/DD/YYYY  HH:mm').datetime.year)
crime_dataframe['month'] = crime_dataframe['OCCURRED ON'].map(lambda x: arrow.get(str(x), 'MM/DD/YYYY  HH:mm').datetime.month)
crime_dataframe['day'] = crime_dataframe['OCCURRED ON'].map(lambda x: arrow.get(str(x), 'MM/DD/YYYY  HH:mm').datetime.day)

# filter to year 2016
crime_dataframe_grouped = crime_dataframe[crime_dataframe.year == 2016]
#set-up count column
crime_dataframe_grouped = crime_dataframe_grouped.groupby(['year', "month", "day", "UCR CRIME CATEGORY"]).aggregate('count')
grouped = crime_dataframe_grouped.reset_index()
grouped_subset = grouped.loc[:, ['year','month','day','UCR CRIME CATEGORY', '100 BLOCK ADDR']]

#the count column is the last column in the df
current_count_header_name = grouped_subset.columns.values[len(grouped_subset.columns.values) -1]
final = grouped_subset.rename(columns = {current_count_header_name: 'count'})

#save to csv
final.to_csv('phx-2016-crime.csv', index=False)
