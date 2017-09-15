'''
Created on Dec, 2016
@author: hugo
'''
from __future__ import absolute_import
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('topics_file', type=str, help='path to the topics file')
    parser.add_argument('-o', '--output', type=str, default='out.png', help='path to the output file')
    args = parser.parse_args()


    #doc_codes = load_json(args.topics_file)
    #doc_labels = load_json(args.output)



if __name__ == '__main__':
    main()