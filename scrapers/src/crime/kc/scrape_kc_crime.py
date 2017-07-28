# Script to scrape kansas city crime data
# (Adapted from existing scrapers by msilb7 and wwymak)
# minor tweaks - KC Crime data is split by year where each year stored in individual urls

import pandas as pd
import arrow

# Construct dataframe to hold years and repective urls
url_year = [2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009]
url_api = ["https://data.kcmo.org/resource/wy8a-bydn.json",
           "https://data.kcmo.org/resource/c6e8-258d.json",
           "https://data.kcmo.org/resource/geta-wrqs.json",
           "https://data.kcmo.org/resource/nsn9-g8a4.json",
           "https://data.kcmo.org/resource/ff6a-bhbu.json",
           "https://data.kcmo.org/resource/xwdv-8y2g.json",
           "https://data.kcmo.org/resource/5u8g-kq4k.json",
           "https://data.kcmo.org/resource/c3qq-bxi5.json",
           "https://data.kcmo.org/resource/3u3f-44ew.json"]

api_urls = pd.DataFrame({'year':url_year, 'url':url_api})

LIMIT_PER_REQ = 10000  # Note: this can be set to entire dataset but request may timeout on slow connection


def kc_crime():
  
    for i in range (2009,2017+1):

        # Setup
        available = True
        offset = 0
        BASE_URL = api_urls.loc[api_urls.year== i, ['url']].values.astype('str')[0,0]
        df = pd.DataFrame()

        # Pull everything available
        print(i)
        while available :
            print( '\rEntries pulled: {}'.format( len( df.index ) ), end='' )
            pageUrl = BASE_URL + '?$limit=' + str( LIMIT_PER_REQ ) + '&$offset=' + str( offset )
            dfTemp = pd.read_json( pageUrl )
            df = df.append( dfTemp, ignore_index=True )
            available = len( dfTemp.index ) > 0
            offset += LIMIT_PER_REQ
        print( )
                
        #crimes are at victim level, grab unique reports of crimes
        df = df.drop_duplicates(subset = ['report_no', 'description', 'reported_date'])
        
        #Keep needed columns for Aggregation
        df = df[['reported_date', 'description']]
        
        #rename
        df.columns = ['crimedate', 'description']

        # Dedicated year, month, day fields
        df['year'] = df['crimedate'].map( lambda x : arrow.get( x ).datetime.year )
        df['month'] = df['crimedate'].map( lambda x : arrow.get( x ).datetime.month )
        df['day'] = df['crimedate'].map( lambda x : arrow.get( x ).datetime.day )

        # Get counts based on columns of interest
        df['count'] = 0
        df = df.groupby( ['year', 'month', 'day', 'description'] ).agg( {'count' : 'count'} )
        df = df.reset_index( )
        df = df.loc[:, ['year', 'month', 'day', 'description', 'count']]
        
        #write files to csv's
        fileName = 'data/kc-{}-crime.csv'.format( i )
        df.to_csv( fileName, index=False )
        print( 'Wrote {} entries to'.format( len( df.index ) ), fileName )
        
kc_crime()