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
from sklearn.decomposition import NMF

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


def generate_doc_codes(model, corpus, output):
    model.minimum_probability = 1e-3
    n_topics = model.num_topics
    doc_codes = {}
    for key, doc_bow in corpus.iteritems():
        code = np.zeros(n_topics)
        for idx, val in model[doc_bow]:
            code[idx] = val
        doc_codes[key] = code.tolist()
    dump_json(doc_codes, output)

    return doc_codes


def show_topics_prob(model, vocab_dict, n_words_per_topic=40):
    topics = []
    for topic in model.components_:
        total = float(np.sum(topic))
        topics.append( [ (vocab_dict[j], topic[j]/total) for j in topic.argsort()[::-1][:n_words_per_topic] ] )
    return topics


def test(args):

    from autoencoder.baseline.lda import load_model

    corpus = load_corpus(args.corpus)
    docs, vocab_dict = corpus['docs'], corpus['vocab']
    vocab_dict = dict([(int(y), x) for x, y in vocab_dict.iteritems()])

    model = load_model(args.load_model)
    model.id2word = vocab_dict
    n_topics = model.num_topics
    model.print_topic(0, topn=10)
    topics = [model.show_topic(i, 40) for i in range(n_topics)]
    
    from PIL import Image
    from wordcloud import WordCloud

    def single_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
        return 'black'

    def random_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
        if random_state is None:
            random_state = Random()
        return "hsl(%d, 80%%, 25%%)" % random_state.randint(0, 255)

    for i in range(len(topics)):
        topic = dict(topics[i])
        wordcloud_img = WordCloud(max_font_size=40, prefer_horizontal=1.0, \
                                  color_func=random_color_func, background_color='white' \
                                  ).generate_from_frequencies(topic).to_image()
        wc_filename = (str(i) + '.' ).join(args.word_cloud.rsplit('.', 1) )
        wordcloud_img.save( wc_filename )
        print 'Saved word cloud file to %s' % wc_filename


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
