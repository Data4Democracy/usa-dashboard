# scraper for Detroit crime with command line arguments
# to specify a year, neighborhood, or zip code 
# (Adapted from existing scrapers by msilb7 and wwymak)

import arrow
import pandas as pd
import argparse


def extract_crime_data(LIMIT_PER_REQ=10000, year=None, zipcode=None):
    # Note: LIMIT_PER_REQ can be set to entire dataset but request may timeout on slow connection    
    
    # Const
    BASE_URL = "https://data.detroitmi.gov/resource/i9ph-uyrp.json?"
     
    # Setup
    available = True
    offset = 0
    df = pd.DataFrame()
    
    # Pull everything available
    while available :
        print('\rEntries pulled: {} '.format(len( df.index)))
        
        if zipcode and year:
            start_year= str(year)
            zipcode = str(zipcode)
            pageUrl = BASE_URL + 'location_zip=' + zipcode +'&$where=incidentdate%20between%20%27'+ \
                        start_year+'-01-01T00:00:00.000%27%20and%20%27' + \
                        start_year + '-12-31T01:00:00.000%27'+ \
                        '&$order=crimeid%20asc' + '&$limit=' + str(LIMIT_PER_REQ) + '&$offset=' + str(offset)
        elif year:
            start_year= str(year)
            pageUrl = BASE_URL +'$where=incidentdate%20between%20%27'+start_year+'-01-01T00:00:00.000%27%20and%20%27' + \
                        start_year + '-12-31T01:00:00.000%27'+ \
                        '&$order=crimeid%20asc' + '&$limit=' + str(LIMIT_PER_REQ) + '&$offset=' + str(offset)

        elif zipcode:
            zipcode = str(zipcode)
            pageUrl = BASE_URL + 'location_zip='+ zipcode + \
                      '&$order=crimeid%20asc' + '&$limit=' + str(LIMIT_PER_REQ) + '&$offset=' + str(offset)
              
             
        else:
            pageUrl = BASE_URL + '&$order=crimeid%20asc' + '&$limit=' + str(LIMIT_PER_REQ) + '&$offset=' + str(offset)

        dfTemp = pd.read_json( pageUrl )
        df = df.append(dfTemp, ignore_index=True)
        available = len(dfTemp.index) > 0
        offset += LIMIT_PER_REQ
    print
    
    # Dedicated year, month, day fields
    df['year'] = df['incidentdate'].map(lambda x : arrow.get(x).datetime.year)
    df['month'] = df['incidentdate'].map(lambda x : arrow.get(x).datetime.month)
    df['day'] = df['incidentdate'].map(lambda x : arrow.get(x).datetime.day)
    
    # Get counts based on columns of interest
    df['count'] = 0
    df = df.groupby(['year', 'month', 'day', 'category']).agg({'count' : 'count'})
    df = df.reset_index()
    df = df.loc[:, ['year', 'month', 'day', 'category', 'count']]
  
    
    # Write out to csv by year
    yearMax = df.loc[:, 'year'].max()
    yearMin = df.loc[:, 'year'].min()
    
    for yr in range(yearMin, yearMax + 1) :
        dfAnnual = df[df['year'] == yr]
        fileName = 'data/det-{}-crime.csv'.format(yr)
        dfAnnual.to_csv(fileName, index=False)
        print( 'Wrote {} entries to'.format(len(dfAnnual.index )), fileName)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--limit', nargs='?', default=10, help='records pulled per request', type=int)
                        
    parser.add_argument('-y','--year', nargs='?', default=None, help='year data to be pulled', type=int)
    
    parser.add_argument('-z','--zip', nargs='?', default=None, help='zipcode data to be pulled', type=int)    
    
    args = parser.parse_args()
    
    extract_crime_data(LIMIT_PER_REQ=args.limit, year=args.year, zipcode=args.zip)
    
if __name__ == '__main__':
    main()
    
    
    
    