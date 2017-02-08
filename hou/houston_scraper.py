import urllib2 as url 
from bs4 import BeautifulSoup
import pandas as pd
import socket

divisions = ['central', 'north', 'northeast', 'eastside']
divisions += ['southcentral', 'clearlake', 'southeast', 'fondren']
divisions += ['midwest', 'southwest', 'westside', 'northwest']
ext_divisions = ['intercontinental', 'hobby']

districts = {}
districts['central'] = ['1a10', '1a20', '1a30', '1a40', '1a50']
districts['central'] += ['2a10', '2a20', '2a30', '2a40', '2a50', '2a60']
districts['north'] = ['3b10', '3b20', '3b30', '3b40', '3b50']
districts['north'] += ['6b10', '6b20', '6b30', '6b40', '6b50', '6b60']
districts['northeast'] = ['7c10', '7c20', '7c30', '7c40', '7c50']
districts['northeast'] += ['8c10', '8c20', '8c30', '8c40', '8c50', '8c60']
districts['northeast'] += ['9c10', '9c20', '9c30', '9c40']
districts['northeast'] += ['24c10', '24c20', '24c30', '24c40', '24c50']
districts['eastside'] = ['11h10', '11h20', '11h30', '11h40', '11h50']
districts['southcentral'] = ['10h10', '10h20', '10h30', '10h40']
districts['southcentral'] += ['10h50', '10h60', '10h70', '10h80']
districts['clearlake'] = ['12d10', '12d20', '12d30', '12d40']
districts['clearlake'] += ['12d50', '12d60', '12d70']
districts['southeast'] = ['13d10', '13d20', '13d30', '13d40']
districts['southeast'] += ['14d10', '14d20', '14d30', '14d40', '14d50']
districts['fondren'] = ['17e10', '17e20', '17e30', '17e40']
districts['midwest'] = ['18f10', '18f20', '18f30', '18f40', '18f50', '18f60']
districts['southwest'] = ['15e10', '15e20', '15e30', '15e40']
districts['southwest'] += ['16e10', '16e20', '16e30', '16e40']
districts['westside'] = ['19g10', '19g20', '19g30', '19g40', '19g50']
districts['westside'] += ['20g10', '20g20', '20g30', '20g40']
districts['westside'] += ['20g50', '20g60', '20g70', '20g80']
districts['northwest'] = ['4f10', '4f20', '4f30', '5f10', '5f20', '5f30', '5f40']

### intercontinental and hobby have a different url schema

months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun']
months += ['jul', 'aug', 'sep', 'oct', 'nov', 'dec']
years = ['09', '10', '11', '12', '13', '14', '15', '16', '17']

total_cols = []

def column_name_clean(s):
	### This function normalizes non-standard column names
	s = s.lower()
	if 'date' in s:
		return 'Date'
	elif 'time' in s:
		return 'Time'
	elif '#' in s:
		return 'Number of Offenses'
	elif 'type' in s:
		return 'Type'
	elif 'block' in s:
		return 'Block Range'
	elif 'street' in s:
		return 'Street Name'
	else:
		return s

def dedupe(lst):
	### This function removes duplicate columns after cleaning, e.g. Type and Offense Type
	for i in xrange(len(lst)):
		count = len([elt for elt in lst[:i] if elt == lst[i]])
		if count > 0:
			lst[i] = lst[i] + str(count+1)
	return lst

columns_to_keep = ['Division', 'District', 'Month', 'Year', 'Date', 'Time', 'Type', 'Street Name', 'Block Range', 'Number of Offenses']

first_page = True
for division in divisions:
	for district in districts[division]:
		for month in months:
			for year in years:
				retry_count = 0
				succeeded = False
				while retry_count < 3 and succeeded == False:
					try:
						base_url = 'http://www.houstontx.gov/police/cs/stats20{}/{}{}/{}{}{}.htm'.format(year, month, year, month, year, district)
						page = url.urlopen(base_url).read()
						table = BeautifulSoup(page, 'html.parser').body.table
						first_row = True
						lst = []
						for row in table.find_all('tr'):
							if first_row:
								first_row = False
								cols = ['Division', 'District', 'Month', 'Year'] + [column_name_clean(elt.getText().encode('utf-8').strip()) for elt in row.find_all('td')]
								cols = dedupe(cols)
							else:
								lst.append([division, district, month, year] + [elt.getText().encode('utf-8').strip() for elt in row.find_all('td')])
								df = pd.DataFrame(lst, columns=cols)
						df = df[[col for col in columns_to_keep if col in df.columns.values]]
						for col in columns_to_keep:
							if col not in df.columns.values:
								df[col] = None
						df.columns = columns_to_keep
						print df.columns.values
						if first_page == True:
							final_df = df
							first_page = False
						else:
							final_df = pd.concat([final_df, df], axis=0)
						succeeded = True
						print final_df.shape
					except url.HTTPError: # 404: some of these are expected; incomplete data
						print district, month, year, '404: Page Not Found.'
						break
					except socket.error:
						retry_count += 1

final_df.to_csv('houston_crime_data.csv')


