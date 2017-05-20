# Script to scrape baltimore crime data
# (Adapted from existing scrapers by msilb7 and wwymak)

import pandas as pd
import arrow

# Const
BASE_URL = "https://data.baltimorecity.gov/resource/4ih5-d5d5.json"
LIMIT_PER_REQ = 10000  # Note: this can be set to entire dataset but request may timeout on slow connection

# Setup
available = True
offset = 0
df = pd.DataFrame( )

# Pull everything available
while available :
	print( '\rEntries pulled: {}'.format( len( df.index ) ), end='' )
	pageUrl = BASE_URL + '?$limit=' + str( LIMIT_PER_REQ ) + '&$offset=' + str( offset )
	dfTemp = pd.read_json( pageUrl )
	df = df.append( dfTemp, ignore_index=True )
	available = len( dfTemp.index ) > 0
	offset += LIMIT_PER_REQ
print( )

# Dedicated year, month, day fields
df['year'] = df['crimedate'].map( lambda x : arrow.get( x ).datetime.year )
df['month'] = df['crimedate'].map( lambda x : arrow.get( x ).datetime.month )
df['day'] = df['crimedate'].map( lambda x : arrow.get( x ).datetime.day )

# Get counts based on columns of interest
df['count'] = 0
df = df.groupby( ['year', 'month', 'day', 'description'] ).agg( {'count' : 'count'} )
df = df.reset_index( )
df = df.loc[:, ['year', 'month', 'day', 'description', 'count']]

# Write out to csv by year
yearMax = df.loc[:, 'year'].max( )
yearMin = df.loc[:, 'year'].min( )
for yr in range( yearMin, yearMax + 1 ) :
	dfAnnual = df[df['year'] == yr]
	fileName = 'data/bal-{}-crime.csv'.format( yr )
	dfAnnual.to_csv( fileName, index=False )
	print( 'Wrote {} entries to'.format( len( dfAnnual.index ) ), fileName )
