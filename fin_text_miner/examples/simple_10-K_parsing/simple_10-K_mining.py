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


import os
import sys

from collections import defaultdict


sys.path.append('../../lib')

# Functions from sec_text_miner handle common tasks
# Code for non-standard tasks, such as choosing the first and last 10-Ks (and a special few in the middle) for a CIK, written in current file

from utils import load_text , save_text , load_csv , save_csv, download
from sec_text_miner.sec_filing_index import download_all_filing_indexes , filter_and_combine_filing_indexes
from sec_text_miner.sec_10K_filing import download_10K_docs
from sec_text_miner.html_parser import get_html_tree , get_simplified_text
from sec_text_miner.page_separator import get_default_page_sep_generators , separate_pages
from sec_text_miner.section_extractor import get_default_section_hdr_generators , separate_sections


def extract_and_save_10K_text( ) :
    
    # We get all CIKs from a given csv file    
    headers , rows = load_csv( 'companies.csv' , headers = [ 'CIK' ] , debug = True )
    ciks = [ int( row[ 0 ] ) for row in rows ]
    
    # Here we show how to get a combined filing index for all 10-K filings by a given set of CIKs    
    filing_index_path = 'filing_index.csv'
    if not os.path.isfile( filing_index_path ) :
        filing_indexes_dir = 'filing_indexes'
        download_all_filing_indexes( filing_indexes_dir )
        filter_and_combine_filing_indexes( load_dir = filing_indexes_dir , save_path = filing_index_path , filter_ciks = ciks , filter_form_types = [ '10-K' ] )
    
    # Choosing the first and last 10-Ks (and a special few in the middle) for a CIK    
    rows = select_rows( filing_index_path )
    
    # Now we download docs within these 10_K filings of type 10-K and EX-13
    for cik , date , filename in rows :        
        if os.path.isfile( '10-K_downloads/' + str( cik ) + '_' + date + '_10-K.txt' ) : continue        
        docs = download_10K_docs( filename )
        for doc_type , doc_text in docs.iteritems( ) :
            save_text( '10-K_downloads/' + str( cik ) + '_' + date + '_' + doc_type + '.txt' , doc_text , debug = True )        

    # Next swe pass each doc through an html parser that fixes malformed html,
    # then extract a simplified version of the html that retains minimal tag and tag attributes
    # that might be necessary for parsing pages, and sections and (numbered & unnumbered) subsections
    for filename in sorted( os.listdir( '10-K_downloads' ) , key = lambda name : int( name.split( '_' , 1 )[ 0 ] ) ) :            
        save_path = '10-K_simplified/' + filename        
        if os.path.isfile( save_path ) : continue        
        text = load_text( '10-K_downloads/' + filename )
        html_tree = get_html_tree( text )
        text = get_simplified_text( html_tree )
        save_text( save_path , text , debug = True )
    
    
    # Now we move on to page separation and section extraction, where we use simplified text as input.
    for filename in sorted( os.listdir( '10-K_simplified' ) , key = lambda name : int( name.split( '_' , 1 )[ 0 ] ) )[ : 10 ] :
        print filename
        text = load_text( '10-K_simplified/' + filename )
        page_sep_generators = get_default_page_sep_generators( text ) # can customize
        pages = separate_pages( text , page_sep_generators , debug = True )
        text = ( '\n\n' + '=' * 40 + '\n\n' ).join( pages ) + '\n'
        save_text( '10-K_paginated/' + filename , text , debug = True )
        text = '\n\n'.join( pages[ : : 2 ] )
        section_hdr_generators = get_default_section_hdr_generators( text ) # can customize
        sections = separate_sections( text , section_hdr_generators , debug = True )
        print


# A change in company name, for a given CIK, might indicate a major structural reorganization.
# Thus, for each company, we download the the last 10-K filing before every name change
# along with the first and the last 10-K filing, which should give us a quick overview of the company.

def select_rows( filing_index_path ) :
    
    cik_to_names = defaultdict( list )
    cik_name_to_date_filenames = defaultdict( list )
    
    headers , rows = load_csv( filing_index_path , headers = [ 'CIK' , 'Company Name' ,'Date Filed' , 'Filename' ] , debug = True )
    for row in rows :
        cik = int( row[ 0 ] ) ; name = row[ 1 ] ; date = row[ 2 ] ; filename = row[ 3 ]
        cik_to_names[ cik ].append( name )
        cik_name_to_date_filenames[ ( cik , name ) ].append( ( date , filename ) )

    rows = [ ]

    # For each CIK,
    for cik in sorted( cik_to_names ) :
        
        # for each company name associated to the CIK,
        for i , name in enumerate( cik_to_names[ cik ] ) :
            
            date_filenames = cik_name_to_date_filenames[ ( cik , name ) ]
                
            # we get download-related info for the last 10-K filing under the given name.
            date , filename = date_filenames[ -1 ]
            rows.append( ( cik , date , filename ) )
            
            # Also, we get download-related info for the first ever 10-K filing
            if i == 0 and len( date_filenames ) > 1 :
                date , filename = date_filenames[ 0 ]
                rows.append( ( cik , date , filename ) )
                
    return rows


if __name__ == '__main__' :
    
    extract_and_save_10K_text( )
    
    