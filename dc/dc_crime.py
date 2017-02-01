# h/t to wwymak for the nyc code that this is based heavily on.
import numpy as np
import pandas as pd
import arrow
import datetime
import urllib
 
#setup variables for year links
yeardict = {
    2016: "http://opendata.dc.gov/datasets/bda20763840448b58f8383bae800a843_26.csv",
    2015: "http://opendata.dc.gov/datasets/35034fcb3b36499c84c94c069ab1a966_27.csv",
    2014: "http://opendata.dc.gov/datasets/6eaf3e9713de44d3aa103622d51053b5_9.csv",
    2013: "http://opendata.dc.gov/datasets/5fa2e43557f7484d89aac9e1e76158c9_10.csv",
    2012: "http://opendata.dc.gov/datasets/010ac88c55b1409bb67c9270c8fc18b5_11.csv",
    2011: "http://opendata.dc.gov/datasets/9d5485ffae914c5f97047a7dd86e115b_35.csv",
    2010: "http://opendata.dc.gov/datasets/fdacfbdda7654e06a161352247d3a2f0_34.csv",
    2009: "http://opendata.dc.gov/datasets/73cd2f2858714cd1a7e2859f8e6e4de4_33.csv",
    2008: "http://opendata.dc.gov/datasets/180d56a1551c4e76ac2175e63dc0dce9_32.csv"
}
minyear = 2016
maxyear = 2016
curryear = minyear
while (curryear <= maxyear):
    rawlink = yeardict[curryear]
    if (curryear == minyear):
        crime_dataframe = pd.read_csv(rawlink)
    else:
        crime_dataframe = crime_dataframe.append(pd.read_csv(rawlink), ignore_index=True)
    curryear = curryear +1
#extract date into columns

crime_dataframe['year'] = crime_dataframe['REPORTDATETIME'].map(lambda x: arrow.get(x).datetime.year)
crime_dataframe['month'] = crime_dataframe['REPORTDATETIME'].map(lambda x: arrow.get(x).datetime.month)
crime_dataframe['day'] = crime_dataframe['REPORTDATETIME'].map(lambda x: arrow.get(x).datetime.day)
#set-up count column
crime_dataframe_grouped = crime_dataframe.groupby(['year', "month", "day", "OFFENSE"]).aggregate('count')
grouped = crime_dataframe_grouped.reset_index()
grouped_subset = grouped.loc[:, ['year','month','day','OFFENSE', 'X']]

#the count column is the last column in the df
current_count_header_name = grouped_subset.columns.values[len(grouped_subset.columns.values) -1]
final = grouped_subset.rename(columns = {current_count_header_name: 'count'})

#save to csv
if (minyear == maxyear):
    final.to_csv('dc-' + str(minyear) + '-crime.csv', index=False)
else:
    final.to_csv('dc-' + str(minyear) + '-' + str(maxyear) + '-crime.csv', index=False)
