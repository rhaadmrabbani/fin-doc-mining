import re

import numpy as np
from numpy import linalg as LA

from collections import defaultdict

from autoencoder.utils.io_utils import dump_json, load_json


doc_name_re = re.compile( r'(?P<year>\d{4})-\d{2}-\d{2}-(?P<cik>\d+)_(?P<section>.+).txt' )

def main():
    
    fail_years_filepath = '../../py13/cik&fys.txt'
    corpus_path = '../../py13/mod_corpus/8-K'
    
    f = open( fail_years_filepath )
    bank_fail_year_lines = f.readlines( )
    f.close( )
    
    
    bank_to_fail_year_map_items = [ tuple( line.strip( ).split( ',' ) ) for line in bank_fail_year_lines ]
    bank_to_fail_year_map_items = [ ( bank , fail_year ) for bank , fail_year in bank_to_fail_year_map_items if fail_year != 'NA' ]
    bank_to_fail_year_map = dict( bank_to_fail_year_map_items )
    
    
    train_corpus = load_json( corpus_path + '/train.corpus' ) ; train_doc_to_bow_map = train_corpus['docs']
    test_corpus = load_json( corpus_path + '/test.corpus' ) ; test_doc_to_bow_map = test_corpus['docs']
    doc_to_bow_map_items = train_doc_to_bow_map.items( ) + test_doc_to_bow_map.items( )
    doc_to_bow_map = dict( doc_to_bow_map_items )
    
    
    train_bank_to_docs_map = load_json( corpus_path + '/train.bank_to_docs_map' )
    test_bank_to_docs_map = load_json( corpus_path + '/test.bank_to_docs_map' )
    bank_to_docs_map_items = train_bank_to_docs_map.items( ) + test_bank_to_docs_map.items( )
    
    bank_to_docs_map_items.sort( )
    i = 1
    while i < len( bank_to_docs_map_items ) :
        bank_prev , docs_prev = bank_to_docs_map_items[ i - 1 ]
        bank , docs = bank_to_docs_map_items[ i ]
        if bank_prev == bank :
            bank_to_docs_map_items[ i - 1 : i + 1 ] = [ ( bank , docs_prev + docs ) ]
            continue
        i += 1
        
    
    simils_pre_fail_avgs = [ ]
    simil_fails = [ ]
    
    for bank , docs in bank_to_docs_map_items :

        if bank in bank_to_fail_year_map :

            fail_year = bank_to_fail_year_map[ bank ]

            year_to_bow_map = { }
            
            for doc in docs :
                
                doc_name_m = doc_name_re.match( doc )
                year = doc_name_m.group( 'year' )
                
                if not year in year_to_bow_map :
                    year_to_bow_map[ year ] = np.array( [ 0 ] * 4000 )
                
                bow = doc_to_bow_map[ doc ]
                for word , count in bow.iteritems( ) :
                    year_to_bow_map[ year ][ int( word ) ] += count
            
            year_to_norm_bow_map = { }
            
            for year , bow in year_to_bow_map.iteritems( ) :
                year_to_norm_bow_map[ year ] = bow / LA.norm( bow )
            
            year_to_norm_bow_map_items = year_to_norm_bow_map.items( )
            year_to_norm_bow_map_items.sort( )
            
            simils_pre_fail = [ ]
            simil_fail = [ ]
            
            i = 1
            while i < len( year_to_norm_bow_map_items ) :
                year_prev , bow_prev = year_to_norm_bow_map_items[ i - 1 ]
                year , bow = year_to_norm_bow_map_items[ i ]
                d = np.dot( bow_prev , bow )
                if year < fail_year :
                    simils_pre_fail.append( d )
                elif year == fail_year :
                    simil_fail.append( d )
                i += 1
                
            if simils_pre_fail and simil_fail :
                simils_pre_fail_avgs.append( np.median( simils_pre_fail ) )
                simil_fails.append( simil_fail[ 0 ] )                
                print bank , ':' , simils_pre_fail_avgs[ -1 ] , simil_fails[ -1 ]
                
    print 'average :' , np.median( simils_pre_fail_avgs ) , np.median( simil_fails  )   
    

if __name__ == "__main__":
    main()
