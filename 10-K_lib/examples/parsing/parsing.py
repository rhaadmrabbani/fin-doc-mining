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


# is a Python2 library
# starting out as a Master's project
# open source a necessity
# so much variation due to human factor of filers and lack of strict submission format
# structured from human perspective
# loosely structured / unstructured text, unlike xml
# major roadblock for prospective researchers
#
# interesting questions
#
# one very simple example, one reflecting more standard use and demonstrating the code's ability to handle multiple 
#
# The following example will demonstrate the download utilities, page separation how to use the 10-K lib to:
#
# 10K , then others

# 10K especially section !a 
# section extraction important
# recently receiving a good degree of attention
# 
# - download and save all quarterly indexes available at SEC's online archive
#   as csv files
#
# - take the CIKs of a set of public companies, and retrieve their 10-K
#   filings, for arbitrarily selected years, using information from the indexes
#   (a CIK is an unique id assigned by SEC to each filing company)
#
# - simplify each downloaded doc, retaining minimal information
#   (must retain information (i.e. html tags) that helps indicate page
#   separation and section/subsection headers, which will be helpful in mending
#   sentences split across pages and in section/subsection level text
#   extraction)
#
# download 10-K filings extracting the
# sections


import os
import sys
from collections import defaultdict


sys.path.append('../../lib')
from utils import load_text , save_text , load_csv , save_csv
from downloader import download_and_save_indexes , download_10K_docs
from htmlparser import get_html_tree , get_simplified_text
from pageparser import split_to_pages


# First, we fetch the CIKs of a set of public companies from a csv file.

headers , rows = load_csv( 'companies.csv' , headers = [ 'CIK' ] , debug = True )
ciks = [ int( row[ 0 ] ) for row in rows ]


# Then we create an index of 10-K filings for those particular CIKs.

save_path = 'filtered_and_combined_index.csv'
if not os.path.isfile( save_path ) :
    
    
    # Quarterly indexes of filings are available at SEC's online archive.    
    # We download all these quarterly indexes.

    download_and_save_indexes( '../../data/SEC_indexes' )
    
    
    # From all downloaded indexes, we select the rows containing info on 10-K
    # filings by our chosen CIKs, and save these rows in a single csv file

    load_filenames = sorted( os.listdir( '../../data/SEC_indexes' ) )
    all_rows = [ ]
    for i , filename in enumerate( load_filenames ) :
        headers , rows = load_csv( '../../data/SEC_indexes/' + filename , debug = True )
        all_rows += [ row for row in rows
                      if int( row[ headers.index( 'CIK' ) ] ) in ciks
                      and row[ headers.index( 'Form Type' ) ] == '10-K' ]
    all_rows.sort( key = lambda row : int( row[ 0 ] ) ) # group by CIK
    save_csv( save_path , headers = headers , rows = all_rows , debug = True )
    

# A change in company name, for a given CIK, might indicate a major structural
# reorganization. Thus, for each company, we download the the last 10-K filing
# before every name change along with the first and the last 10-K filing, which
# should give us a quick overview of the company.

cik_to_names = defaultdict( list )
cik_name_to_date_filenames = defaultdict( list )
info_for_download = [ ]

headers , rows = load_csv( 'filtered_and_combined_index.csv' ,
                           headers = [ 'CIK' , 'Company Name' ,'Date Filed' , 'Filename' ] ,
                           debug = True )
for row in rows :
    cik = int( row[ 0 ] ) ; name = row[ 1 ] ; date = row[ 2 ] ; filename = row[ 3 ]
    cik_to_names[ cik ].append( name )
    cik_name_to_date_filenames[ ( cik , name ) ].append( ( date , filename ) )
    
# For each CIK,
for cik in sorted( cik_to_names ) :
    
    # for each company name associated to the CIK,
    for i , name in enumerate( cik_to_names[ cik ] ) :
        
        date_filenames = cik_name_to_date_filenames[ ( cik , name ) ]
            
        # we get download-related info for the last 10-K filing under the given name.
        date , filename = date_filenames[ -1 ]
        info_for_download.append( ( cik , date , filename ) )
        
        # Also, we get download-related info for the first ever 10-K filing
        if i == 0 and len( date_filenames ) > 1 :
            date , filename = date_filenames[ 0 ]
            info_for_download.append( ( cik , date , filename ) )
        

# We download and save 10-K and EX-13x docs from the chosen 10-K filings. The
# text included in the 10-K doc is usually all we need. However, sometimes, and
# not too infrequently, the text of the important MDA section (section 7 in
# 10-K) is attached by reference in EX-13.

for cik , date , filename in info_for_download :
    
    if os.path.isfile( '10-K_downloads/' + str( cik ) + '_' + date + '_10-K.txt' ) : continue
    
    docs = download_10K_docs( filename )
    for doc_type , doc_text in docs.iteritems( ) :
        save_text( '10-K_downloads/' + str( cik ) + '_' + date + '_' + doc_type + '.txt' , doc_text , debug = True )


# Some 10-K and EX-13 docs, especially earlier ones, are in plain text, whereas
# most are in HTML. Before we proceed onto page separation, we first simplify
# each downloaded doc to a more human readable form, retaining as little
# information as we need to move forward. To be specific, we try to retain
# every HTML tag that indicate section/subsection headers and page
# separation points. In plain text files, headers are usually indicated through
# capitalization, and page separation points through page numbers and, often, a
# <PAGE> tag.

# For a low subsection level textual analysis, locating section/subsection
# headers is essential. Identifying page separation points helps to eliminate
# junk text and also mend sentences split across pages, which will be helpful
# for sentence level analysis.

# For analyses treating each doc as a bag-of-words, a high-quality page
# separation step might not be essential, and this simplified text form might
# suffice.

for filename in sorted( os.listdir( '10-K_downloads' ) , key = lambda name : int( name.split( '_' , 1 )[ 0 ] ) ) :

    save_path = '10-K_simplified/' + filename
    
    if os.path.isfile( save_path ) : continue
    
    text = load_text( '10-K_downloads/' + filename )
    html_tree = get_html_tree( text )
    text = get_simplified_text( html_tree )
    save_text( save_path , text , debug = True )


# Now we move on to page separation, where we use simplified text as input.

for filename in sorted( os.listdir( '10-K_simplified' ) , key = lambda name : int( name.split( '_' , 1 )[ 0 ] ) ) :
    
    print filename
    text = load_text( '10-K_simplified/' + filename )
    pages = split_to_pages( text , debug = True )
    text = ( '\n\n' + '=' * 40 + '\n\n' ).join( pages ) + '\n'
    save_text( '10-K_paginated/' + filename , text , debug = True )
    
    