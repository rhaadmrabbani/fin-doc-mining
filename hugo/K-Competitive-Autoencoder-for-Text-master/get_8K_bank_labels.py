import argparse
import re


from autoencoder.utils.io_utils import load_json, dump_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--label', type=str, required=True, help='path to the input label file')
    parser.add_argument('-o', '--output', type=str, required=True, help='path to the output file')
    args = parser.parse_args()

    bank_re = re.compile('-(?P<bank>\d+)_')
    dump_json(dict( (name, bank_re.search(name).group('bank') ) for name in load_json(args.label) ), args.output)
    label_dict = load_json(args.label)

    labels = set( label_dict[ name ] for name in label_dict )
 
    print 'size: ' + str(len(label_dict) )

    print '#classes: ' + str(len(labels) )
    print labels
    print

if __name__ == '__main__':
    main()
