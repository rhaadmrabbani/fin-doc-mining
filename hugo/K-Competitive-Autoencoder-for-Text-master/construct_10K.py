'''
Created on Dec, 2016
@author: hugo
'''

import os
import sys
from autoencoder.preprocessing.preprocessing import construct_train_test_corpus, generate_8k_doc_labels , generate_8k_bank_to_docs_map, get_all_files

def main():
    usage = 'python construct_corpus.py [in_path] [out_path]'
    try:
        in_path = '../../py13/multifiltered_sections/10-K'#sys.argv[1]
        out_path ='../../py13/corpus/10-K' #sys.argv[2]
    except:
        print usage
        sys.exit()
    train_corpus, test_corpus = construct_train_test_corpus(in_path, out_path, threshold=5, topn=4000)
    
    
    train_labels = generate_8k_doc_labels(train_corpus['docs'].keys(), os.path.join(out_path, 'train.labels'))
    test_labels = generate_8k_doc_labels(test_corpus['docs'].keys(), os.path.join(out_path, 'test.labels'))
    train_bank_to_docs_map = generate_8k_bank_to_docs_map( train_corpus['docs'].keys(), os.path.join(out_path, 'train.bank_to_docs_map') )
    test_bank_to_docs_map = generate_8k_bank_to_docs_map( test_corpus['docs'].keys(), os.path.join(out_path, 'test.bank_to_docs_map') )
    

if __name__ == "__main__":
    main()
 