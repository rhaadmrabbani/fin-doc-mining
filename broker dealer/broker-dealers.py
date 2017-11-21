import os

from collections import defaultdict

from lib.file_utils import save_text
from lib.csv_utils import csv_read
from lib.html_utils import get_html, get_simplified_text

from lib.sec_search_by_sic import download_company_list
from lib.sec_form_indexes import download_form_indexes , filter_and_combine_form_indexes
from lib.sec_forms import download_10K
from lib.sec_docs import get_docs


sics = [ 6200 , 6211 , 6221 , 6282 ]


'''
for sic in sics : download_company_list( sic , 'company_list_' + str( sic ) + '.csv' )

download_form_indexes( 'sec_form_indexes' )

filter_ciks = [ int( cik ) for sic in sics for row in csv_read( 'company_list_' + str( sic ) + '.csv' , [ 'cik' ] ) for cik in row ]
filter_form_types = [ '10-K' ]
load_paths = [ 'sec_form_indexes/' + f for f in os.listdir( 'sec_form_indexes' ) ]
filter_and_combine_form_indexes( filter_ciks , filter_form_types , load_paths , 'combined_form_index.csv' )

for row in csv_read( 'combined_form_index.csv' , [ 'Filename' , 'CIK' , 'Date Filed' ] ) : download_10K( row[ 0 ] , 'sec_10Ks/' + row[ 1 ] + '_' + row[ 2 ] + '.txt' )
'''

'''
cik_to_names = defaultdict( set )
cik_to_dates = defaultdict( list )
for row in csv_read( 'combined_form_index.csv' , [ 'CIK' , 'Date Filed' , 'Company Name' ] ) :
    cik_to_dates[ row[ 0 ] ].append( row[ 1 ][ : 4 ] )
    cik_to_names[ row[ 0 ] ].add( row[ 2 ] )

for cik in sorted( cik_to_names ) : cik_to_names[ cik ] = list( cik_to_names[ cik ] )

save_file = open( 'list.txt' , 'w' )
for cik in sorted( list( cik_to_names ) , key = lambda cik : cik_to_names[ cik ][ 0 ] ) : save_file.write( '{}\n{} : {}\n\n'.format( ' | '.join( cik_to_names[ cik ] ) , cik , ', '.join( cik_to_dates[ cik ] ) ) )
save_file.close( )
'''

for file_name in os.listdir( 'sec_10Ks' )[ : 1] :
    print file_name
    docs = get_docs( 'sec_10Ks/' + file_name , [ '10-K' ] )
    for i , ( doc_type , doc_text ) in enumerate( docs ) :        
        html = get_html( doc_text )
        text = get_simplified_text( html )        
        save_text( 'simple_10Ks/' + file_name + ( '' if i == 0 else str( i ) ) , text )
