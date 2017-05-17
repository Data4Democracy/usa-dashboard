import requests
import pandas as pd
from bs4 import BeautifulSoup  
import re
import arrow
import datetime

# Below script is designed to parse the crime data from the Louisville Police Department's
# website. It loads https://data.louisvilleky.gov/dataset/crime-data and finds the annual
# crime reports in CSV. 

webpage = requests.get('https://data.louisvilleky.gov/dataset/crime-data')

soup = BeautifulSoup(webpage.content,'html.parser')

hrefs = soup.findAll('a', href=True)

#Find all csvs on the page that are annual reports using regex and beautifulsoup#

annual_report_files = []

for link in hrefs:
	file_name = link['href']
	if re.search('^https', file_name):
		if re.search('.csv$', file_name):
			if re.search('[0-9]{4}', file_name):
				annual_report_files.append(file_name)


#Download annuals report files and merge into one large dataframe by appending each year#

it = 1
df = None
for file in annual_report_files:
	if it == 1:
		print(file)
		last_year = re.search(r"([0-9]{4})", file).group(1)
		df = pd.read_csv(file)
		it += 1 
	else:
		print(file)
		ndf = pd.read_csv(file)
		df = df.append(ndf,ignore_index=True)
		it +=1 
		first_year = re.search(r"([0-9]{4})", file).group(1)



#As of February 10th, 2007, the Lousiville's website has a duplicate of the 2012 csv
#as the 2009 data. The below serves to drop the duplicate rows that are added by
#repeating the 2012 data in the 2009 CSV without adding edge case information to
#the above code. 

df = df.drop_duplicates()

#The data from the Louisville police department has data for surrounding cities as well. This filters
#out any other city besides just Louisville. 

df = df[df['CITY'] == 'LOUISVILLE']

#Create dataframe with just incident date and category for highlevel analysis


df = df[['DATE_OCCURED','CRIME_TYPE']]

#Drop any rows that lack either an incident date or a category
df = df.dropna()

#Transform incident date column into three columns for year, month, and date
df['year'] = df['DATE_OCCURED'].map(lambda x: arrow.get(x, ['YYYY-MM-DD HH:mm:ss']).datetime.year)
df['month'] = df['DATE_OCCURED'].map(lambda x: arrow.get(x, ['YYYY-MM-DD HH:mm:ss']).datetime.month)
df['day'] = df['DATE_OCCURED'].map(lambda x: arrow.get(x, ['YYYY-MM-DD HH:mm:ss']).datetime.day)


df = df[['year','month','day','CRIME_TYPE']]

count_frame = df.groupby(['year','month','day','CRIME_TYPE'])['CRIME_TYPE'].aggregate('count')

grouped = count_frame.reset_index(name='count')

#crime data has some incidents from outside the reported years. These are dropped here.

grouped = grouped[grouped['year'] >= int(first_year)]
grouped = grouped[grouped['year'] <= int(last_year)] 

#rename 'CRIME_TYPE' column to 'crime_type' for consistency 

final = grouped.rename(columns={'CRIME_TYPE': 'crime_type'})

#save csv
final.to_csv('data/louisville_crime_data_'+first_year+'-'+last_year+'.csv',index=False)


