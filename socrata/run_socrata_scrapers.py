# Driver script to handle socrata scrapers

# lib
import json
import argparse

# src
from SocrataScraper import SocrataScraper
from PostgresUtils import CreateEngine

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
	engine = None
	if configJson['writeSQL'] :
		try :
			engine = CreateEngine( 'postgresql://{}:{}@{}/{}'.format(
				auth.authPostgres['user'],
				auth.authPostgres['pass'],
				auth.authPostgres['host'],
				auth.authPostgres['db'] ) )

		except Exception as e :
			print( 'Exception on SQL engine setup: {}'.format( repr( e ) ) )

	if not engine :
		print( 'Warning: Postgres connection not configured' )

	# Run each active scraper
	for configScraper in configJson['scrapers'] :
		try :
			# include global config fields
			configScraper['limitPerReq'] = configJson['limitPerReq']
			configScraper['writeCSV'] = configJson['writeCSV']
			configScraper['writeSQL'] = configJson['writeSQL']

			if configScraper['active'] :
				# Configure and run scraper
				scraper = SocrataScraper( configScraper, engine )
				scraper.Run( )

		except Exception as e :
			print( 'Exception on scraper run: {}'.format( repr( e ) ) )

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
