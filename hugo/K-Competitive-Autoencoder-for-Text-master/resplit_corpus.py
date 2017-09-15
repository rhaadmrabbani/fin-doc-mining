import re
import os , os.path
import sys
from autoencoder.preprocessing.preprocessing import generate_8k_doc_labels , generate_8k_bank_to_docs_map
from autoencoder.utils.io_utils import dump_json, load_json


doc_name_re = re.compile( r'(?P<year>\d{4})-\d{2}-\d{2}-(?P<cik>\d+)_(?P<section>.+).txt' )

def main():
    '''
    orig_corpus_path = '../../py13/corpus/10-K'
    mod_section_re = re.compile( r'1A' )
    mod_train_years = [ str( y ) for y in range( 2005 , 2010 ) ]
    mod_corpus_path = '../../py13/mod_corpus/10-K_1A'
    '''
    
    '''
    orig_corpus_path = '../../py13/corpus/10-K'
    mod_section_re = re.compile( r'7|7A' )
    mod_train_years = [ str( y ) for y in range( 2005 , 2010 ) ]
    mod_corpus_path = '../../py13/mod_corpus/10-K_7'
    '''    
    
    '''
    orig_corpus_path = '../../py13/corpus/10-K'
    mod_section_re = re.compile( r'.*' )
    mod_train_years = [ str( y ) for y in range( 2005 , 2010 ) ]
    mod_corpus_path = '../../py13/mod_corpus/10-K'
    '''
    
    #'''
    orig_corpus_path = '../../py13/corpus/8-K'
    mod_section_re = re.compile( r'.*' )
    mod_train_years = [ str( y ) for y in range( 2005 , 2010 ) ]
    mod_corpus_path = '../../py13/mod_corpus/8-K'
    #'''        
    
    orig_train_corpus = load_json( orig_corpus_path + '/train.corpus' )
    orig_train_docs, vocab_dict = orig_train_corpus['docs'], orig_train_corpus['vocab']  
    
    orig_test_corpus = load_json( orig_corpus_path + '/test.corpus' )
    orig_test_docs = orig_test_corpus['docs']
    
    docs_items = orig_train_docs.items( ) + orig_test_docs.items( )
    
    mod_train_docs_items = [ ]
    mod_test_docs_items = [ ]
    
    for doc_name , bow in docs_items :
        
        doc_name_m = doc_name_re.match( doc_name )
        year = doc_name_m.group( 'year' )
        cik = doc_name_m.group( 'cik' )
        section = clean_section_name( doc_name_m.group( 'section' ) )
        
        if mod_section_re.match( section ) :
            ( mod_train_docs_items if year in mod_train_years else mod_test_docs_items ).append( ( doc_name , bow ) )
    
    mod_train_docs = dict( mod_train_docs_items )
    mod_test_docs = dict( mod_test_docs_items )
    
    if not os.path.exists( mod_corpus_path ) :
        os.makedirs( mod_corpus_path )
    
    mod_train_corpus = {'docs' : mod_train_docs , 'vocab' : vocab_dict }
    dump_json( mod_train_corpus , mod_corpus_path + '/train.corpus' )    
    
    mod_test_corpus = {'docs' : mod_test_docs , 'vocab' : vocab_dict }
    dump_json( mod_test_corpus , mod_corpus_path + '/test.corpus' )
    
    generate_8k_doc_labels( mod_train_docs , mod_corpus_path + '/train.labels' )
    generate_8k_doc_labels( mod_test_docs , mod_corpus_path + '/test.labels' )
    
    generate_8k_bank_to_docs_map( mod_train_docs , mod_corpus_path + '/train.bank_to_docs_map' )
    generate_8k_bank_to_docs_map( mod_test_docs , mod_corpus_path + '/test.bank_to_docs_map' )


section_re = re.compile( r'(?P<num>[\dil]+)(?P<suff>.*)' , re.I )
section_num_1_re = re.compile( r'[il]' , re.I )
section_junk_suff_re = re.compile( r'[^a-z]' , re.I )

def clean_section_name( section ) :
    
    section_m = section_re.match( section )
    
    num = section_m.group( 'num' )
    num = section_num_1_re.sub( '1' , num )
    
    suff = section_m.group( 'suff' )
    suff = section_junk_suff_re.sub( '' , suff ).upper( )
    
    return num + suff


if __name__ == "__main__":
    main()
