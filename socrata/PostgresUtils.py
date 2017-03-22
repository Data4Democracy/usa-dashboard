# Utilities for interfacing with postgres db

# lib
import pandas as pd
from sqlalchemy import create_engine

# Update existing table by replacing duplicate rows and inserting new ones
def UpdateTable( engineSQL, tableName, dfNew ) :
	# Validate
	if not engineSQL :
		print( 'SQL engine not configured' )
		return False
	if not tableName :
		print( 'Table name required' )
		return False
	if dfNew.empty :
		print( 'New dataframe empty' )
		return False

	# Read table if exists
	try :
		with engineSQL.connect( ) as conn :
			dfCurr = pd.read_sql_table( tableName, conn )
			if any( dfCurr.columns.values != dfNew.columns.values ) :
				print( 'Table columns do not match. Returning...' )
				return False

			# Do insert/replace
			trans = conn.begin( )
			print( 'Updating {}...'.format( tableName ) )
			try :
				countNew = 0
				countUpdated = 0
				for index, entry in dfNew.iterrows( ) :
					# Check for existing entry
					duplicate = dfCurr.loc[(dfCurr['year'] == entry['year'])
										   & (dfCurr['month'] == entry['month'])
										   & (dfCurr['day'] == entry['day'])
										   & (dfCurr['metric'] == entry['metric'])]

					if duplicate.empty :
						# Insert new entry
						conn.execute(
							'INSERT INTO {} (year, month, day, metric, count) VALUES ({}, {}, {}, \'{}\', {})'.format(
								tableName, entry['year'], entry['month'], entry['day'], entry['metric'], entry['count']
							) )
						countNew += 1

					elif len( duplicate.index ) == 1 and duplicate.iloc[0, :]['count'] != entry['count'] :
						# Update duplicate with new count
						conn.execute(
							'UPDATE {} SET count = {} WHERE year = {} AND month = {} AND day = {} AND metric = \'{}\''.format(
								tableName, entry['count'], entry['year'], entry['month'], entry['day'], entry['metric']
							) )
						countUpdated += 1

				trans.commit( )
				print( 'Finished update on {}. New entries: {}, Updated entries: {}'.format(
					tableName, countNew, countUpdated ) )
				return True

			except Exception as e :
				print( 'Update of table {} failed: {}'.format( tableName, e ) )
				trans.rollback( )
				return False

	except Exception as e :
		print( 'Caught exception: {}. Trying to create new table...'.format( e ) )
		return CreateTable( engineSQL, tableName, dfNew )

def CreateTable( engineSQL, tableName, dfNew ) :
	# Validate
	if not engineSQL :
		print( 'SQL engine not configured' )
		return False
	if not tableName :
		print( 'Table name required' )
		return False
	if dfNew.empty :
		print( 'New dataframe empty' )
		return False

	# Connect
	with engineSQL.connect( ) as conn, conn.begin( ) :
		# Write and give access to Mode bot
		print( 'Writing new table: {} ({} rows) to Postgres database...'.format(
			tableName, len( dfNew.index ) ) )
		dfNew.to_sql( tableName, conn, index=False )
		conn.execute( 'GRANT ALL PRIVILEGES ON TABLE {} to awsuser'.format( tableName ) )
		print( 'Done.' )

# Creates engine, but returns None if creds are invalid
def CreateEngine( dbURL ) :
	engine = create_engine( dbURL )
	testConn = engine.connect( )
	if testConn :
		print( 'Postgres connection verified.' )
		return engine
	else :
		print( 'Warning: Postgres connection test failed.' )
		return None
