# MIT License
#
# Copyright (c) 2017 Rhaad M. Rabbani
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import csv
import re
import os
import urllib2


# HELPER FUNCTION(S) BEGIN
    
def prepare_save_path( save_path ) :

    save_dir = os.path.dirname( save_path )

    if not save_dir : pass # save_dir is current directory
    elif not os.path.isdir( save_dir ) : os.makedirs( save_dir ) 
    
# HELPER FUNCTION(S) END


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


# Utility function that:
# (i) loads csv from load_path, 
# (ii) filters columns by headers if headers provided, and
# (iii) returns csv as the tuple ( headers , rows )

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

