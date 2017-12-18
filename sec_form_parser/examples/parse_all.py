# Please run download_all.py first



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



form_downloads_dir = 'data/10-K_downloads'
interm_repr_dir = 'data/10-K_interm_repr'
paginated_repr_dir = 'data/10-K_paginated'
sections_dir = 'data/10-K_sections'

key_to_sort_filenames_by_cik = lambda name : int( name.split( '_' , 1 )[ 0 ] )


if __name__ == '__main__' :
    
    
    # Pre-parse to generate intermediate representation
    
    for filename in sorted( os.listdir( form_downloads_dir ) , key = key_to_sort_filenames_by_cik ) :
        save_path = interm_repr_dir + '/' + filename
        if os.path.isfile( save_path ) : continue
        print filename
        text = load_text( form_downloads_dir + '/' + filename )
        doc_type_to_text_map = extract_10K_docs( text ) # a doc's text is a doc without its metadata tags
        doc_type , doc_text = doc_type_to_text_map.items( )[ 0 ] # if file was downloaded using download_all.py, the file is guaranteed to contain a single doc
        doc_text = pre_parse( doc_text )
        save_text( save_path , doc_text , debug = True )
        
        
    for filename in sorted( os.listdir( interm_repr_dir ) , key = key_to_sort_filenames_by_cik ) :
        print filename
        text = load_text( interm_repr_dir + '/' + filename )
        pages = parse_pages( text , debug = True )
        text = ''.join( [ str( page ) for page in pages ] )
        save_text( paginated_repr_dir + '/' + filename , text , debug = True )
        if filename.endswith( '_10-K.txt' ) :
            item_num_to_text_map = parse_sections( pages , debug = True )
            for item_num , item_text in item_num_to_text_map.iteritems( ) :
                save_text( '{}/{}/{}.txt'.format( sections_dir , filename[ : -4 ] , item_num ) , item_text , debug = True )        
        print
        
        