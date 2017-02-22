import urllib2
import pandas as pd
from pandasql import sqldf

def getData(year):

  print "starting with %s"%year

  url = "https://data.sfgov.org/resource/cuks-n6tp.csv?$where=Date%%20between%%20%%27%s-01-01%%27%%20and%%20%%27%s-12-31%%27&$limit=1000000&$order=date"%(year,year);

  crimeData = pd.read_csv(url, encoding='utf-8');

  outData = sqldf( """
    SELECT 
      STRFTIME( "%Y", date) AS year, 
      STRFTIME( "%m", date) AS month,
      STRFTIME( "%d", date) AS day, 
      category, COUNT(*) AS count 
    FROM 
      crimeData 
    GROUP BY 
      date, category ORDER BY date, category;
  """, locals() )

  outData.to_csv("%s.csv"%year,index=False)

  print "done with %s"%year

for year in range( 2003, 2018 ):
  getData(year)
