# h/t to wwymak for the nyc code that this is based heavily on.
import numpy as np
import pandas as pd
import arrow
import datetime
import urllib
 
#setup variables for paging
#Date Range
mindate = "2016-01-01"
maxdate = "2017-01-01"
limit = 50000
offsetval = limit
#find total number of records to iterate through
apilink = "https://data.cityofchicago.org/resource/6zsd-86xi.json"
countquery = (apilink + "?$where=date>'"+ mindate +"'%20AND%20date<'"+ maxdate + "'&$select=count(*)")
numrecords = pd.read_json(countquery)
#get total number of records as an integer
numr = numrecords.iloc[0,0]

#Apply to Query string
qonestr = apilink + "?$where=date>'"+ mindate +"'%20AND%20date<'"+ maxdate + "'&$limit=" + str(limit)
crime_dataframe = pd.read_json(qonestr)	
#Page through data, appemd to the dataframe
while (offsetval < numr):
    qtwostr = qonestr + "&$offset=" + str(offsetval)
    crime_dataframe = crime_dataframe.append(pd.read_json(qtwostr), ignore_index=True)
    offsetval = offsetval + limit
#extract date into columns
crime_dataframe['year'] = crime_dataframe['date'].map(lambda x: arrow.get(x).datetime.year)
crime_dataframe['month'] = crime_dataframe['date'].map(lambda x: arrow.get(x).datetime.month)
crime_dataframe['day'] = crime_dataframe['date'].map(lambda x: arrow.get(x).datetime.day)
#set-up count column
crime_dataframe_grouped = crime_dataframe.groupby(['year', "month", "day", "primary_type"]).aggregate('count')
grouped = crime_dataframe_grouped.reset_index()
grouped_subset = grouped.loc[:, ['year','month','day','primary_type', 'arrest']]

# the count column is the last column in the df
current_count_header_name = grouped_subset.columns.values[len(grouped_subset.columns.values) -1]
final = grouped_subset.rename(columns = {current_count_header_name: 'count'})

# save to csv
final.to_csv('chi-2016-crime.csv', index=False)
