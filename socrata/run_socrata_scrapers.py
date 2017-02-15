# Driver script to handle socrata scrapers

# lib
import json
import argparse

# src
from socrata.SocrataScraper import SocrataScraper

def main( ) :
	args = ParseArguments( )

	with open( args['config'] ) as configFile :
		configJson = json.load( configFile )

	for configScraper in configJson['scrapers'] :
		try :
			# include global config fields
			configScraper['appToken'] = configJson['appToken']
			configScraper['limitPerReq'] = configJson['limitPerReq']

			# Configure and run scraper
			scraper = SocrataScraper( configScraper )
			scraper.Run( )

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
