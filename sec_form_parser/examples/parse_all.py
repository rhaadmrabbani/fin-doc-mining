# parse_all.py
# Author(s): Rhaad M. Rabbani (2017)

# This file demonstrates the library calls to pre-parse, parse pages and parse sections.
# parse_all.py expects a collection 10-K form documents in a single directory.
# Please run download_all.py first if you do not have a directory of 10-K downloads ready.



import os
import sys



sys.path.append('../lib')
from utils.utils import *
from utils.io_utils import *
from utils.text_utils import *
from download import extract_10K_docs
from pre_parse import pre_parse
from parse_pages import parse_pages
from parse_sections import parse_sections



form_downloads_dir = 'data/10-K_downloads' # directory containing downloaded 10-K forms

interm_repr_dir = 'data/10-K_interm_repr' # directory in which we save the easy-to-read intermediate form of each document

paginated_repr_dir = 'data/10-K_paginated' # directory in which we save the paginated form (shows page body, header, footer and page number) of each document

sections_dir = 'data/10-K_sections' # directory in which, for each 10-K document, we save the sections we extract under a sub-folder

key_to_sort_filenames_by_cik = lambda name : int( name.split( '_' , 1 )[ 0 ] )



if __name__ == '__main__' :
    
    
    # Pre-parse to generate easy-to-read intermediate representation.
    
    for filename in sorted( os.listdir( form_downloads_dir ) , key = key_to_sort_filenames_by_cik ) :
        
        save_path = interm_repr_dir + '/' + filename
        if os.path.isfile( save_path ) : continue
        
        print filename
        
        # Load text from a multi-document 10-K form or an individual 10-K or EX-13x document.
        text = load_text( form_downloads_dir + '/' + filename )
        
        # Extract relevant document(s) (of type 10-K and EX-13x).
        doc_type_to_text_map = extract_10K_docs( text )
        
        # A document's text is a document without its metadata tags.
        doc_type , doc_text = doc_type_to_text_map.items( )[ 0 ] # if file was downloaded using download_all.py, the file is guaranteed to contain a single document
        
        # Call pre-parse to obtain easy-to-read intermediate representation
        doc_text = pre_parse( doc_text )
        save_text( save_path , doc_text , debug = True )
        
    
    # Feed document text to page parser to obtain pages,
    # then feed pages to section parser to obtain sections.
    
    for filename in sorted( os.listdir( interm_repr_dir ) , key = key_to_sort_filenames_by_cik ) :
        
        print filename
        
        text = load_text( interm_repr_dir + '/' + filename )
        
        # Parse pages.
        pages = parse_pages( text , debug = True )
        text = ''.join( [ str( page ) for page in pages ] )
        save_text( paginated_repr_dir + '/' + filename , text , debug = True )
        
        # Parse sections for documents of type 10-K.
        if filename.endswith( '_10-K.txt' ) :
            item_num_to_text_map = parse_sections( pages , debug = True )
            for item_num , item_text in item_num_to_text_map.iteritems( ) :
                save_text( '{}/{}/{}.txt'.format( sections_dir , filename[ : -4 ] , item_num ) , item_text , debug = True )        
        print
        


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
