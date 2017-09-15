'''
Created on Nov, 2016

@author: hugo

'''
from __future__ import absolute_import
import argparse
from os import path
import timeit
import math
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.externals import joblib
from ionmf.factorization.model import iONMF

from autoencoder.preprocessing.preprocessing import load_corpus
from autoencoder.utils.io_utils import dump_json, write_file
from autoencoder.baseline.lda import calc_pairwise_cosine, calc_pairwise_dev


def generate_doc_codes(model, doc_keys, doc_bow, output):
    codes = model.predict(doc_bow)
    doc_codes = dict( [ (doc_keys[i], codes[i].tolist() ) for i in range(len(doc_keys) ) ] )
    dump_json(doc_codes, output)


def show_topics_prob(model, vocab_dict, n_words_per_topic=10):
    topics = []
    for i, topic in enumerate(model.components_):
        total = float(np.sum(topic))
        topics.append( [ (vocab_dict[j], topic[j]/total) for j in topic.argsort()[::-1][:n_words_per_topic] ] )
    return topics


def train(args):
    corpus = load_corpus(args.corpus)
    docs, vocab_dict = corpus['docs'], corpus['vocab']
    indptr = [0]
    indices = []
    data = []
    doc_keys = docs.keys()
    for k in doc_keys:
        for idx, count in docs[k].iteritems():
            indices.append(int(idx) )
            data.append(count)
        indptr.append(len(indices) )
        del docs[k]
    doc_bow = csr_matrix((data, indices, indptr), dtype=int)
    vocab_dict = dict([(int(y), x) for x, y in vocab_dict.iteritems()])

    n_samples = doc_bow.shape[0]
    np.random.seed(0)
    val_idx = np.random.choice(range(n_samples), args.n_val, replace=False)
    train_idx = list(set(range(n_samples)) - set(val_idx))
    dbow_train = doc_bow[train_idx].toarray()
    dbow_val = doc_bow[val_idx].toarray()
    dbow_train = dict( [ ('data_source_' + str(i + 1), dbow_train[i] ) for i in range(dbow_train.shape[0] ) ] )
    dbow_val = dict( [ ('data_source_' + str(i + 1), dbow_val[i] ) for i in range(dbow_val.shape[0] ) ] )
    del doc_bow

    start = timeit.default_timer()
    onmf = iONMF(rank=args.n_topics, max_iter=args.n_iter, alpha=1.0)
    onmf.fit(dbow_train)
    joblib.dump(pca, args.save_model)
    print 'runtime: %ss' % (timeit.default_timer() - start)

    if args.output:
        doc_keys = np.array(doc_keys)
        generate_doc_codes(onmf, doc_keys[train_idx], dbow_train, args.output)
        generate_doc_codes(onmf, doc_keys[val_idx], dbow_val, args.output + '.val')
        print 'Saved doc codes file to %s and %s' % (args.output, args.output + '.val')

def test(args):
    corpus = load_corpus(args.corpus)
    docs, vocab_dict = corpus['docs'], corpus['vocab']
    indptr = [0]
    indices = []
    data = []
    doc_keys = docs.keys()
    for k in doc_keys:
        for idx, count in docs[k].iteritems():
            indices.append(int(idx))
            data.append(count)
        indptr.append(len(indices) )
        del docs[k]
    doc_bow = csr_matrix((data, indices, indptr), dtype=int).toarray()
    doc_bow = dict( [ ('data_source_' + str(i + 1), doc_bow[i] ) for i in range(doc_bow.shape[0] ) ] )
    vocab_dict = dict([(int(y), x) for x, y in vocab_dict.iteritems()])

    onmf = joblib.load(args.load_model)
    generate_doc_codes(onmf, doc_keys, doc_bow, args.output)
    print 'Saved doc codes file to %s' % args.output

    if args.save_topics:
        topics_prob = show_topics_prob(onmf, vocab_dict)
        save_topics_prob(topics_prob, args.save_topics)
        # topics = show_topics(lda)
        # write_file(topics, args.save_topics)
        print 'Saved topics file to %s' % args.save_topics

    if args.calc_distinct:
        # mean, std = calc_pairwise_cosine(lda)
        # print 'Average pairwise angle (pi): %s (%s)' % (mean / math.pi, std / math.pi)
        sd = calc_pairwise_dev(lda)
        print 'Average squared deviation from 0 (90 degree): %s' % sd

def save_topics_prob(topics_prob, out_file):
    try:
        with open(out_file, 'w') as datafile:
            for topic in topics_prob:
                datafile.write(' + '.join(["%s * %s" % each for each in topic]) + '\n')
                datafile.write('\n')
    except Exception as e:
        raise e

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true', help='train flag')
    parser.add_argument('-nv', '--n_val', type=int, default=1000, help='size of validation set (default 1000)')
    parser.add_argument('--corpus', required=True, type=str, help='path to the corpus file')
    parser.add_argument('-nt', '--n_topics', type=int, help='num of topics')
    parser.add_argument('-iter', '--n_iter', type=int, help='num of iterations')
    parser.add_argument('-sm', '--save_model', type=str, default='lda.mod', help='path to the output model')
    parser.add_argument('-lm', '--load_model', type=str, help='path to the trained model')
    parser.add_argument('-o', '--output', type=str, help='path to the output doc codes file')
    parser.add_argument('-st', '--save_topics', type=str, help='path to the output topics file')
    parser.add_argument('-cd', '--calc_distinct', action='store_true', help='calc average pairwise angle')
    args = parser.parse_args()

    if args.train:
        if not args.n_topics:
            raise Exception('n_topics arg needed in training phase')
        train(args)
    else:
        if not args.output:
            raise Exception('output arg needed in test phase')
        if not args.load_model:
            raise Exception('load_model arg needed in test phase')
        test(args)

if __name__ == '__main__':
    main()
