import os
import re
import csv_utils



filename_re = re.compile( r'.*-(?P<cik>\d+).txt' )
ciks = set( [ int( filename_re.match( filename ).group( 'cik' ) ) for filename in os.listdir( 'edgar_forms/10-K' ) if os.stat( 'edgar_forms/10-K/' + filename ).st_size > 0 ] )


old_ciks = csv_utils.parse_csv( 'old/cik&fys.txt' )
old_ciks = set( [ int( cik ) for cik , date in old_ciks ] )