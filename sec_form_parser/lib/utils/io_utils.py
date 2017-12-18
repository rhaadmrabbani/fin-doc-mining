# lib/utils/io_utils.py
# Author: Rhaad M. Rabbani (2017)
# This file contains I/O-related utility functions intended for use by the user.



import csv
import re
import os
import urllib2



################################################################
## I/O-related utility functions intended for use by the user ##
################################################################



# Utility function that loads and returns text from load_path

def load_text( load_path , debug = False ) :
    
    if debug : print 'Loading text from ' + load_path + ' ...'
    
    load_file = open( load_path )
    text = load_file.read( )
    load_file.close( )
    
    return text



# Utility function that saves text to save_path

def save_text( save_path , text , debug = False ) :
    
    if debug : print 'Saving text to ' + save_path + ' ...'
    
    prepare_save_path( save_path )
    
    save_file = open( save_path , 'w' )
    save_file.write( text )
    save_file.close( )



# Utility function that loads csv from load_path, filters columns by headers if headers provided,
# and returns csv as the tuple ( headers , rows )

def load_csv( load_path , headers = None , debug = False ) :
    
    if debug : print 'Loading csv from ' + load_path + ' ...'
    
    load_file = open( load_path , 'rb' )
    
    if headers :
        rows = [ [ row[ header ] for header in headers ] for row in csv.DictReader( load_file ) ]
    else :
        rows = list( csv.reader( load_file ) )
        headers = rows[ 0 ]
        rows = rows[ 1 : ]
    
    load_file.close( )
    
    return headers , rows



# Utility function that saves headers and rows of csv to save_path

def save_csv( save_path , headers = None , rows = None , debug = False ) :
    
    if debug : print 'Saving csv to ' + save_path + ' ...'
    
    prepare_save_path( save_path )
    
    save_file = open( save_path , 'wb' )
    
    csv_writer = csv.writer( save_file , delimiter = ',' , quotechar = '"' , quoting = csv.QUOTE_MINIMAL )
    if headers : csv_writer.writerow( headers )
    if rows :
        for row in rows : csv_writer.writerow( row )
    
    save_file.close( )



# Utility function that downloads raw text from an url and returns it

def download( url , debug = False ) :
    
    if debug : print 'Downloading ' + url + ' ...'
        
    response = urllib2.urlopen( url )
    raw = response.read( )
    
    return raw



#######################################################
## Helper functions not intended for use by the user ##
#######################################################



def prepare_save_path( save_path ) :

    save_dir = os.path.dirname( save_path )

    if not save_dir : pass # save_dir is the current directory
    elif not os.path.isdir( save_dir ) : os.makedirs( save_dir ) 
