
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


def test(args):

    from autoencoder.core.ae import load_ae_model
    from random import Random

    corpus = load_corpus(args.corpus)
    vocab, docs = corpus['vocab'], corpus['docs']
    n_vocab = len(vocab)

    model = load_ae_model(args.load_model)
    vocab = dict((v, k) for (k, v) in vocab.iteritems())

    weights = model.get_weights()[0]

    topics = []
    weights = model.get_weights()[0]
    for idx in range(model.output_shape[1]):
        token_idx = np.argsort(weights[:, idx])[::-1][:40]
        topics.append([(vocab[x], weights[x, idx]) for x in token_idx])
    
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
