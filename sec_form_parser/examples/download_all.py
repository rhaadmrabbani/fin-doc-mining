# Use this file to first download SEC indexes, then filter and combine those indexes,
# and finally download the relevant docs within 10-K forms.
# This file demonstrates the use of download-related tools in the library.



import os
import sys
from collections import defaultdict


sys.path.append('../lib')
from utils.utils import *
from utils.io_utils import *
from download import download_indexes , combine_indexes , download_10K_docs



companies_path = 'data/companies.csv'
combined_index_path = 'data/combined_index.csv'
indexes_dir = 'data/sec_indexes'
form_downloads_dir = 'data/10-K_downloads'



if __name__ == '__main__' :
    
    
    # Download SEC indexes, and filter by CIK and combine those indexes
    
    headers , rows = load_csv( companies_path , headers = [ 'CIK' ] , debug = True )
    ciks = [ int( row[ 0 ] ) for row in rows ]    
    
    if not os.path.isfile( combined_index_path ) : # Will not re-download and combine indexes after first run
        download_indexes( indexes_dir )
        combine_indexes( load_dir = indexes_dir , save_path = combined_index_path , filter_ciks = ciks , filter_form_types = [ '10-K' ] )
    
    
    # Keep only the first (since 2006) and the last 10-K per CIK to reduce the total number of files we handle in this example
    
    cik_to_rows_map = defaultdict( list )
    headers , rows = load_csv( combined_index_path , headers = [ 'CIK' , 'Company Name' ,'Date Filed' , 'Filename' ] , debug = True )
    for row in rows :
        if row[ 2 ] >= '2006-01-01' : cik_to_rows_map[ int( row[ 0 ] ) ].append( row )
    rows = [ row for cik in sorted( cik_to_rows_map ) for row in cik_to_rows_map[ cik ][ : 1 ] + cik_to_rows_map[ cik ][ -1 : ] ]
    
    
    # Download relevant docs from 10-K forms and save
    
    for cik , name , date , filename in rows :
        if os.path.isfile( '{}/{}_{}_10-K.txt'.format( form_downloads_dir , cik , date ) ) : continue        
        doc_type_to_doc_map = download_10K_docs( filename )
        for doc_type , doc in doc_type_to_doc_map.iteritems( ) :
            save_text( '{}/{}_{}_{}.txt'.format( form_downloads_dir , cik , date , doc_type ) , doc , debug = True )
            
            
    # You may now proceed to run parse_all.py or parse_one.py
    