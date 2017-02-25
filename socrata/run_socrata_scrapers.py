# Driver script to handle socrata scrapers

# lib
import json
import argparse
from sqlalchemy import create_engine

# src
from SocrataScraper import SocrataScraper

# authentication
try :
	import config as auth
except :
	print( 'Warning: failed to import config.py' )

def main( ) :
	args = ParseArguments( )

	with open( args['config'] ) as configFile :
		configJson = json.load( configFile )

	# Setup up sql engine
	if configJson['writeSQL'] :
		try :
			engine = create_engine( 'postgresql://{}:{}@{}/{}'.format(
				auth.authPostgres['user'],
				auth.authPostgres['pass'],
				auth.authPostgres['host'],
				auth.authPostgres['db'] ) )
			# verify auth
			testConn = engine.connect( )
			if testConn :
				print( 'Postgres connection verified.' )
			else :
				print( 'Warning: Postgres connection test failed.' )
				engine = None

		except Exception as e :
			print( 'Exception: {}'.format( repr( e ) ) )
			engine = None

	# Run each active scraper
	for configScraper in configJson['scrapers'] :
		try :
			# include global config fields
			configScraper['limitPerReq'] = configJson['limitPerReq']
			configScraper['writeCSV'] = configJson['writeCSV']
			configScraper['writeSQL'] = configJson['writeSQL']

			if configScraper['active'] :
				# Configure and run scraper
				scraper = SocrataScraper( configScraper )
				scraper.Run( engine )

		except Exception as e :
			print( 'Exception: {}'.format( repr( e ) ) )

# Command Line Arguments
def ParseArguments( ) :
	# Define arguments
	parser = argparse.ArgumentParser( )
	parser.add_argument( '-c', '--config', help='Path to configuration file',
						 default='socrata-config.json' )

	# Parse arguments and return
	args = vars( parser.parse_args( ) )

	return args

if __name__ == '__main__' :
	main( )
