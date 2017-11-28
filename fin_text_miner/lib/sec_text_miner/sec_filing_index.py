import os
import re
import sys


sys.path.append('../lib')
from utils import load_text , save_text , load_csv , save_csv, download


directory_re = re.compile( r'<a href="(?P<directory>\w+)/"><img [^>]*? alt="folder icon">' , re.I | re.S )

index_junk_re = re.compile( r'^.*?(\r?\n *){3,}|(?<=\n)-+\r?\n' , re.S )

nl_re = re.compile( r'\r?\n' )


# Function that downloads and saves (as csv files) all quarterly filing indexes available at SEC's online archive

def download_all_filing_indexes( save_dir ) :

    listing_by_year = download( 'https://www.sec.gov/Archives/edgar/full-index/' )
    
    for m in directory_re.finditer( listing_by_year ) :
        
        year = m.group( 'directory' )        
        listing_by_qtr = download( 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/' )
        
        for m in directory_re.finditer( listing_by_qtr ) :
    
            qtr = m.group( 'directory' )            
            save_path = save_dir + '/' + year + '_' + qtr + '.csv'
            
            if os.path.isfile( save_path ) : continue
      
            idx = download( 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/' + qtr + '/master.idx' , debug = True )
            idx = index_junk_re.sub( '' , idx )
            rows = [ line.split( '|' ) for line in nl_re.split( idx ) if line ]
            
            save_csv( save_path , rows = rows )


def filter_and_combine_filing_indexes( load_dir , save_path , filter_ciks = None , filter_form_types = None ) :
    
    if filter_ciks : filter_ciks = set( filter_ciks )
    if filter_form_types : filter_form_types = set( filter_form_types )
    
    all_rows = [ ]
    
    for i , filename in enumerate( sorted( os.listdir( load_dir ) ) ) :
        
        headers , rows = load_csv( load_dir + '/' + filename , debug = True )
        
        if i == 0 :
            cik_col = headers.index( 'CIK' )
            form_type_col = headers.index( 'Form Type' )
            
        all_rows += [ row for row in rows
                      if ( filter_ciks == None or int( row[ cik_col ] ) in filter_ciks )
                      and ( filter_form_types == None or row[ form_type_col ] in filter_form_types ) ]
        
    all_rows.sort( key = lambda row : int( row[ cik_col ] ) ) # group by CIK
    
    save_csv( save_path , headers = headers , rows = all_rows , debug = True )
            