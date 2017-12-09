# Not ready for use


# This example demonstrates parsing a single SEC 10-K form.
# The location of the 10-K or EX-13x form must be provided as a command line argument.
# e.g. python parse_one.py data/10-K_downloads/7084_1994-09-27_10-K.txt
# If you do not have any downloaded forms, you may run download_all.py first.



import argparse
import sys


sys.path.append('../lib')
from utils import *



def parse_one( filepath ) :

    # The pre-parser generates an intermediate representation of the form that is acceptable to the parser.
    # For special cases, the user may write their own pre-parsing method
    
    pass


if __name__ == '__main__' :
    
    arg_parser = argparse.ArgumentParser( )
    arg_parser.add_argument( "filepath" , help = "location of the downloaded 10-K or EX-13x form to be parsed" , type = str )
    args = arg_parser.parse_args( )
    
    parse_one( args.filepath )
