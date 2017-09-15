import csv_utils



firm_data = csv_utils.parse_csv( 'edgar_firm_data_by_sic.csv' )
ciks = set( [ int( cik ) for cik , name , sic , st in firm_data[ 1 : ] ] )



out = open( 'edgar_10-K_index_by_sic.idx' , 'w' )
out.write( 'CIK|Company Name|Form Type|Date Filed|Filename\n' )

for year in range( 1993 , 2017 ) :
    for qtr in range( 1 , 5 ) :
        print year , qtr
        for line in csv_utils.parse_csv( 'edgar_form_indexes/' + str( year ) + '_QTR' + str( qtr ) + '.idx' , sep = r'\|' )[ 1 : ] :
            cik , name , form_type , date , link = line
            if int( cik ) in ciks and form_type == '10-K' :
                out.write( '|'.join( line ) + '\n' )

out.close( )
