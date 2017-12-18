# download_all.py
# Author(s): Rhaad M. Rabbani (2017)

# The SEC (The US Securities and Exchange Commission) requires every publicly-traded US company to file form 10-K, an annual report to shareholders, and a host of other forms.
# We do not provide any content from the SEC. We only include links in our code. Our library makes it easy for the user to download desired 10-K forms.
# This file demonstrates the use of download-related tools provided in the library to download 10-K forms from SEC's site.



import os
import sys
from collections import defaultdict



sys.path.append('../lib')
from utils.utils import *
from utils.io_utils import *
from utils.text_utils import *
from download import download_indexes , combine_indexes , download_10K_docs



companies_path = 'data/companies.csv' # path to file containing info for selected companies

indexes_dir = 'data/sec_indexes' # directory in which we dump all SEC form filing indexes

combined_index_path = 'data/combined_index.csv' # path where we save combined index file

form_downloads_dir = 'data/10-K_downloads' # directory in which we save all our downloaded 10-K documents



if __name__ == '__main__' :
    
    
    # SEC assigns a unique id called CIK to each company.
    # First, we read in CIKs from a file.
    headers , rows = load_csv( companies_path , headers = [ 'CIK' ] , debug = True ) # load_csv will only read thecolumn titled CIK
    ciks = [ int( row[ 0 ] ) for row in rows ] # each row only contains CIK
    
    
    # Next we:
    # (i) download SEC form filing indexes,
    # (ii) combine the indexes in a single index file, filtering by CIK (the CIKs from the file) and form-type (10-K) during the process.  
    if not os.path.isfile( combined_index_path ) :
        download_indexes( indexes_dir )
        combine_indexes( load_dir = indexes_dir , save_path = combined_index_path , filter_ciks = ciks , filter_form_types = [ '10-K' ] )
      
      
    # Load all rows from the combined index file.
    headers , rows = load_csv( combined_index_path , headers = [ 'CIK' , 'Company Name' ,'Date Filed' , 'Filename' ] , debug = True )    
    
    
    # Keep only the first (since 2006) and the last 10-K form per CIK to reduce the total number of files we handle in this example.
    cik_to_rows_map = defaultdict( list )
    for row in rows :
        if row[ 2 ] >= '2006-01-01' : cik_to_rows_map[ int( row[ 0 ] ) ].append( row )
    rows = [ row for cik in sorted( cik_to_rows_map ) for row in cik_to_rows_map[ cik ][ : 1 ] + cik_to_rows_map[ cik ][ -1 : ] ]
    
    
    # Each 10-K filing consists of several documents.
    # Download relevant documents for each selected 10-K form (documents of type 10-K and EX-13x) and save. 
    for cik , name , date , filename in rows :
        if os.path.isfile( '{}/{}_{}_10-K.txt'.format( form_downloads_dir , cik , date ) ) : continue        
        doc_type_to_doc_map = download_10K_docs( filename )
        for doc_type , doc in doc_type_to_doc_map.iteritems( ) :
            save_text( '{}/{}_{}_{}.txt'.format( form_downloads_dir , cik , date , doc_type ) , doc , debug = True )
            
            
    # We may now proceed to run parse_all.py.



# MIT License
#
# Copyright (c) 2017 Rhaad M. Rabbani
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,  OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
