# Utilities for interfacing with postgres db

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
		with engineSQL.connect( ) as conn, conn.begin( ) :
			dfCurr = pd.read_sql_table( tableName, conn )
			if any( dfCurr.columns.values != dfNew.columns.values ) :
				print( 'Table columns do not match. Returning...' )
				return False

			# Do insert/replace
			# TODO

			# Merge with new data, drop duplicated keeping new values
			# dfSQL = dfSQL.append( dfMain, ignore_index=True )
			# dfSQL.drop_duplicates( subset=['year', 'month', 'day', 'metric'], keep='last', inplace=True )

			return True

	except Exception as e :
		print( 'Table: {} does not exist. Creating new... {}'.format( tableName, e ) )
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
