# Socrata Scraper class
# (Adapted from existing scrapers by msilb7 and wwymak)

import pandas as pd
import arrow

class SocrataScraper :
	def __init__( self, config ) :
		# Unload json config
		self.appToken = config['appToken']
		self.limitPerReq = config['limitPerReq']
		self.name = config['name']
		self.endpoints = config['endpoints']
		self.dateFields = config['dateFields']
		self.metricFields = config['metricFields']

		# Set date-time bounds
		if config['startDate'] :
			self.startDate = arrow.get( config['startDate'] )
		else :
			self.startDate = arrow.get( '1970-01-01' )
		if config['endDate'] :
			self.endDate = arrow.get( config['endDate'] )
		else :
			self.endDate = arrow.utcnow( )

		print( 'Constructed SocrataScraper for {} ({} -> {})'.format( self.name, self.startDate.format( 'YYYY-MM-DD' ),
																	  self.endDate.format( 'YYYY-MM-DD' ) ) )

	def Run( self ) :
		print( 'Running scraper...' )
		if not self.Validate( ) :
			print( 'Shutting down.' )
			return

		# Cummulative dataframe for scraper
		dfMain = pd.DataFrame( )

		# Run on each endpoint
		for i, e in enumerate( self.endpoints ) :
			print( 'Hitting: {}'.format( e ) )
			offset = 0
			available = True
			dfEndpoint = pd.DataFrame( )

			# Pull everything available
			while available :
				print( '\rTotal entries pulled: {}'.format( len( dfEndpoint.index ) + len( dfMain.index ) ), end='' )

				pageUrl = (e + '?$limit=' + str( self.limitPerReq ) + '&$offset=' + str( offset )
						   + '&$where=' + self.dateFields[i] + '%20between%20'
						   + self.startDate.format( "'YYYY-MM-DDTHH:mm:ss'" ) + '%20and%20'
						   + self.endDate.format( "'YYYY-MM-DDTHH:mm:ss'" ))

				dfTemp = pd.read_json( pageUrl )
				dfEndpoint = dfEndpoint.append( dfTemp, ignore_index=True )
				available = len( dfTemp.index ) > 0
				offset += self.limitPerReq

			if len( dfEndpoint.index ) == 0 :
				print( )
				continue

			# Dedicated year, month, day fields
			dfEndpoint['year'] = dfEndpoint[self.dateFields[i]].map(
				lambda x : arrow.get( x ).datetime.year )
			dfEndpoint['month'] = dfEndpoint[self.dateFields[i]].map(
				lambda x : arrow.get( x ).datetime.month )
			dfEndpoint['day'] = dfEndpoint[self.dateFields[i]].map(
				lambda x : arrow.get( x ).datetime.day )

			# Get only columns of interest
			dfEndpoint.rename( columns={self.metricFields[i] : 'metric'}, inplace=True )
			dfEndpoint = dfEndpoint.loc[:, ['year', 'month', 'day', 'metric']]

			# TODO: Convert metric at endpoint level to be uniform across all datasets of this type (ie. UCR)
			#
			# Add to main
			dfMain = dfMain.append( dfEndpoint, ignore_index=True )
			print( )

		# Get counts across all endpoints
		dfMain['count'] = 0
		dfMain = dfMain.groupby( ['year', 'month', 'day', 'metric'] ).agg( {'count' : 'count'} )
		dfMain = dfMain.reset_index( )

		# Write out to csv by year
		yearMax = dfMain.loc[:, 'year'].max( )
		yearMin = dfMain.loc[:, 'year'].min( )
		for yr in range( yearMin, yearMax + 1 ) :
			dfAnnual = dfMain[dfMain['year'] == yr]
			fileName = 'data/{}-{}.csv'.format( self.name, yr )
			dfAnnual.to_csv( fileName, index=False )
			print( 'Wrote {} entries to'.format( len( dfAnnual.index ) ), fileName )

	def Validate( self ) :
		n = len( self.endpoints )
		if not n :
			print( 'No endpoints specified.' )
			return False

		if n != len( self.dateFields ) or n != len( self.metricFields ) :
			print( 'Inconsistent endpoint config array lengths.' )
			return False

		return True
