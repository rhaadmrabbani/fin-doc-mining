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
from sklearn.decomposition import PCA

from autoencoder.preprocessing.preprocessing import load_corpus
from autoencoder.utils.io_utils import dump_json, write_file
from autoencoder.baseline.lda import calc_pairwise_cosine, calc_pairwise_dev


from collections import Counter
topic_ratings = Counter()

def generate_doc_codes(model, doc_keys, doc_bow, output):
    codes = model.transform(doc_bow)
    doc_codes = dict( [ (doc_keys[i], codes[i].tolist() ) for i in range(len(doc_keys) ) ] )
    dump_json(doc_codes, output)

    for topic_idx in [ np.fabs(codes[i]).argsort()[::-1][0] for i in range(len(doc_keys) ) ]:
        topic_ratings[topic_idx] += 1


def show_topics_prob(model, vocab_dict, n_words_per_topic=40):
    topics = []
    for topic in model.components_:
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
    del doc_bow

    start = timeit.default_timer()
    pca = PCA(n_components=args.n_topics).fit(dbow_train)
    joblib.dump(pca, args.save_model)
    print 'runtime: %ss' % (timeit.default_timer() - start)

    if args.output:
        doc_keys = np.array(doc_keys)
        generate_doc_codes(pca, doc_keys[train_idx], dbow_train, args.output)
        generate_doc_codes(pca, doc_keys[val_idx], dbow_val, args.output + '.val')
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
    vocab_dict = dict([(int(y), x) for x, y in vocab_dict.iteritems()])

    pca = joblib.load(args.load_model)
    generate_doc_codes(pca, doc_keys, doc_bow, args.output)
    print 'Saved doc codes file to %s' % args.output

    if args.save_topics:
        topics_prob = show_topics_prob(pca, vocab_dict)
        save_topics_prob(topics_prob, args.save_topics)
        # topics = show_topics(lda)
        # write_file(topics, args.save_topics)
        print 'Saved topics file to %s' % args.save_topics

        if args.word_cloud:
            from PIL import Image
            from wordcloud import WordCloud
            from random import Random
            def random_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
                if random_state is None:
                    random_state = Random()
                return "hsl(%d, 80%%, 25%%)" % random_state.randint(0, 255)
            topic_idxs = map(lambda (a, b): a, topic_ratings.most_common(10) )
            for i in range(len(topic_idxs) ):
                topic_idx = topic_idxs[i]
                wordcloud_img = WordCloud(max_font_size=40, prefer_horizontal=1.0, \
                                color_func=random_color_func, background_color='white' \
                                ).generate_from_frequencies(dict(topics_prob[topic_idx]) ).to_image()
                wc_filename = (str(i) + '.' ).join(args.word_cloud.rsplit('.', 1) )
                wordcloud_img.save( wc_filename )
                print 'Saved word cloud file to %s' % wc_filename


    if args.calc_distinct:
        # mean, std = calc_pairwise_cosine(lda)
        # print 'Average pairwise angle (pi): %s (%s)' % (mean / math.pi, std / math.pi)
        sd = calc_pairwise_dev(lda)
        print 'Average squared deviation from 0 (90 degree): %s' % sd

def save_topics_prob(topics_prob, out_file):
    '''
    try:
        with open(out_file, 'w') as datafile:
            for topic in topics_prob:
                datafile.write(' + '.join(["%s * %s" % each for each in topic]) + '\n')
                datafile.write('\n')
    except Exception as e:
        raise e
    '''
    dump_json(topics_prob, out_file)

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
    parser.add_argument('-wc', '--word_cloud', type=str, help='path to the output word cloud file')
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
