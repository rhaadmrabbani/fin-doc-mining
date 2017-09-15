from __future__ import absolute_import
import argparse
import re

from autoencoder.preprocessing.preprocessing import load_corpus
from autoencoder.utils.io_utils import load_file, write_file

doc_name_re = re.compile(r'(?P<y>\d+)-(?P<m>\d+)-(?P<d>\d+)-(?P<bank>\d+)_(?P<sec>.*?)\.txt')

def get_fail_bank_years(doc_names, fail_years):
    doc_name_re_matches = [ doc_name_re.match(n) for n in doc_names ]
    bank_years = set([ (m.group('bank'), m.group('y')) for m in doc_name_re_matches ])
    return [ (bank, year) for bank, year in bank_years if bank in fail_years and fail_years[bank] == year ]
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fail_years', type=str, help='path to bank year to fail year file')
    parser.add_argument('train_corpus', type=str, help='path to the train corpus file')
    parser.add_argument('test_corpus', type=str, help='path to the test corpus file')  
    args = parser.parse_args()

    fail_years = dict(filter(lambda (bank, year): year != 'NA', \
                             [ tuple(l[0].split(',')) for l in load_file(args.fail_years) ]))
    
    train_corpus = load_corpus(args.train_corpus)
    train_docs, vocab_dict = train_corpus['docs'], train_corpus['vocab']
    
    test_corpus = load_corpus(args.test_corpus)    
    test_docs = test_corpus['docs']
    
    train_bank_years = get_fail_bank_years(train_docs.keys(), fail_years)
    test_bank_years = get_fail_bank_years(test_docs.keys(), fail_years)

    print len(train_bank_years)
    print len(test_bank_years)

    failedfile = set(fail_years.items()) - set(train_bank_years) - set(test_bank_years)
    print len(failedfile)
    print failedfile
    
if __name__ == '__main__':
    main()
