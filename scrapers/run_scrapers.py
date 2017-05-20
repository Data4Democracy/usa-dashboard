# Driver script to run all scrapers and dump into postgres

# lib
import argparse

def main( ) :
	args = ParseArguments( )
	print( 'Running scrapers...' )

# Command Line Arguments
def ParseArguments( ) :
	# Define arguments
	parser = argparse.ArgumentParser( )
	parser.add_argument( '-c', '--config', help='Path to configuration file',
						 default='config.json' )

	# Parse arguments and return
	args = vars( parser.parse_args( ) )

	return args

if __name__ == '__main__' :
	main( )
