import numpy as np
import pandas as pd
import arrow

'''
taking nyc scraper as template
'''

# getting data
url = "https://data.seattle.gov/resource/hapq-73pk.csv?$limit=18446744073"
print(url)
crime_dataframe = pd.read_csv(url)

# creating date dimensions
crime_dataframe['year'] = crime_dataframe['report_date'].map(lambda x: arrow.get(x).datetime.year)
crime_dataframe['month'] = crime_dataframe['report_date'].map(lambda x: arrow.get(x).datetime.month)
crime_dataframe['day'] = crime_dataframe['report_date'].map(lambda x: arrow.get(x).datetime.day)

# aggregating data (sum of stat_value)
crime_dataframe_grouped = crime_dataframe.groupby(['year', "month", "day", "crime_type"]).agg({'stat_value': np.sum})
grouped = crime_dataframe_grouped.reset_index()

# removing columns we dont need
grouped_subset = grouped.iloc[:, 0:5]
current_count_header_name = grouped_subset.columns.values[len(grouped_subset.columns.values) -1]

# format column headers and saving to .csv
final = grouped_subset.rename(columns = {current_count_header_name: 'count'})
final.to_csv('data/sea-crime.csv', index=False)
