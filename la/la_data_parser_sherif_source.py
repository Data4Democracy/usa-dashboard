import requests
import pandas as pd
from bs4 import BeautifulSoup  
import re
import arrow
import datetime

# Below script is designed to parse the crime data from the LA County Sheriff's Department's
# website. It loads http://shq.lasdnews.net/CrimeStats/CAASS/desc.html and finds the annual
# crime reports in CSV. 

webpage = requests.get('http://shq.lasdnews.net/CrimeStats/CAASS/desc.html')

soup = BeautifulSoup(webpage.content,'html.parser')

hrefs = soup.findAll('a', href=True)

#Find all csvs on the page that are annual reports using regex and beautifulsoup#

annual_report_files = []

for link in hrefs:
	file_name = link['href']
	if re.search('^[0-9]{4}', file_name):
		annual_report_files.append(file_name)

print(annual_report_files)

#Download annuals report files and merge into one large dataframe by appending each year#

it = 1
df = None
for file in annual_report_files:
	if it == 1:
		print(file)
		first_year = file[0:4]
		df = pd.read_csv('http://shq.lasdnews.net/CrimeStats/CAASS/'+file)
		print (it)
		it += 1 
	else:
		print(file)
		ndf = pd.read_csv('http://shq.lasdnews.net/CrimeStats/CAASS/'+file)
		df = df.append(ndf,ignore_index=True)
		print(it)
		it +=1 
		last_year = file[0:4]

#Create dataframe with just incident date and category for highlevel analysis

df = df[['INCIDENT_DATE','CATEGORY']]

#Drop any rows that lack either an incident date or a category
df = df.dropna()

#Transform incident date column into three columns for year, month, and date
df['year'] = df['INCIDENT_DATE'].map(lambda x: arrow.get(x, ['MM/DD/YYYY HH:mm:ss']).datetime.year)
df['month'] = df['INCIDENT_DATE'].map(lambda x: arrow.get(x, ['MM/DD/YYYY HH:mm:ss']).datetime.month)
df['day'] = df['INCIDENT_DATE'].map(lambda x: arrow.get(x, ['MM/DD/YYYY HH:mm:ss']).datetime.day)


df = df[['year','month','day','CATEGORY']]

count_frame = df.groupby(['year','month','day','CATEGORY'])['CATEGORY'].aggregate('count')

grouped = count_frame.reset_index(name='count')

#crime data has some incidents from outside the reported years. These are dropped here.

grouped = grouped[grouped['year'] >= int(first_year)]
grouped = grouped[grouped['year'] <= int(last_year)] 

#rename 'CATEGORY' column to 'category' for consistency 

final = grouped.rename(columns={'CATEGORY': 'category'})

#save csv
final.to_csv('data/la_crime_data_'+first_year+'-'+last_year+'.csv',index=False)


