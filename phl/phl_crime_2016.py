
# coding: utf-8


# h/t to wwymak for the nyc code that this is based heavily on.
import numpy as np
import pandas as pd
import arrow
import datetime
import urllib
 
#setup variables for paging
#find total number of records to iterate through
countquery = ('https://data.phila.gov/resource/sspu-uyfa.json?$$app_token=QUiKJ4ZSXVHerTpOYAIqt7uf3&$select=count(*)')
numrecords = pd.read_json(countquery)
#get total number of records as an integer
numr = numrecords.iloc[0,0]
limit = 50000
offsetval = limit
#Date Range
mindate = "2015-12-31"
maxdate = "2017-01-01"
#Apply to Query string
qonestr = "https://data.phila.gov/resource/sspu-uyfa.json?$where=dispatch_date>'"+ mindate +"'%20AND%20dispatch_date<'"+ maxdate + "'&$$app_token=QUiKJ4ZSXVHerTpOYAIqt7uf3&$limit=" + str(limit)
crime_dataframe = pd.read_json(qonestr)	
#Page through data, appemd to the dataframe
while (offsetval < (numr - limit)):
    qtwostr = qonestr + "&$offset=" + str(offsetval)
    crime_dataframe = crime_dataframe.append(pd.read_json(qtwostr), ignore_index=True)
    offsetval = offsetval + limit
#extract date into columns
crime_dataframe['year'] = crime_dataframe['dispatch_date'].map(lambda x: arrow.get(x).datetime.year)
crime_dataframe['month'] = crime_dataframe['dispatch_date'].map(lambda x: arrow.get(x).datetime.month)
crime_dataframe['day'] = crime_dataframe['dispatch_date'].map(lambda x: arrow.get(x).datetime.day)
#set-up count column
crime_dataframe_grouped = crime_dataframe.groupby(['year', "month", "day", "text_general_code"]).aggregate('count')
grouped = crime_dataframe_grouped.reset_index()
grouped_subset = grouped.loc[:, ['year','month','day','text_general_code', 'dc_dist']]

# the count column is the last column in the df
current_count_header_name = grouped_subset.columns.values[len(grouped_subset.columns.values) -1]
final = grouped_subset.rename(columns = {current_count_header_name: 'count'})

# save to csv
final.to_csv('phl-2016-crime.csv', index=False)

