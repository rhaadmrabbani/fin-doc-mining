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


import urllib2
import re
import os.path

from collections import defaultdict

from csv_utils import csv_read , csv_write


folder_re = re.compile( r'<a href="(?P<folder>\w+)/"><img [^>]*? alt="folder icon">' , re.I | re.S )

junk_re = re.compile( r'^.*?(\r?\n *){3,}|(?<=\n)-+\r?\n' , re.S )

nl_re = re.compile( r'\r?\n' )


def download_form_indexes( save_dir ) :

    url = 'https://www.sec.gov/Archives/edgar/full-index/'
    print url 
    response = urllib2.urlopen( url )
    html = response.read( )
    
    if not os.path.isdir( save_dir ) : os.makedirs( save_dir )
    
    for m in folder_re.finditer( html ) :
        
        year = m.group( 'folder' )
        
        url = 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/'
        print url        
        response = urllib2.urlopen( url )
        html = response.read( )
        
        for m in folder_re.finditer( html ) :
    
            qtr = m.group( 'folder' )      
            save_path = save_dir + '/' + year + '_' + qtr + '.csv'
            
            if os.path.isfile( save_path ) : continue
      
            url = 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/' + qtr + '/master.idx'
            print url
            response = urllib2.urlopen( url )
            html = response.read( )
            
            html = junk_re.sub( '' , html )
            csv_write( save_path , rows = [ line.split( '|' ) for line in nl_re.split( html ) if line ] )
            
            
def filter_and_combine_form_indexes( filter_ciks , filter_form_types , load_paths , save_path ) :
    
    filter_ciks = set( filter_ciks )
    filter_form_types = set( filter_form_types )
    headers = [ 'CIK' , 'Company Name' , 'Form Type' , 'Date Filed' , 'Filename' ]
    
    cik_to_rows = defaultdict( list )
    
    for load_path in load_paths :
        
        print load_path
        
        for row in csv_read( load_path , headers = headers ) :
            cik = int( row[ 0 ] )
            form_type = row[ 2 ]
            if cik in filter_ciks and form_type in filter_form_types : cik_to_rows[ cik ].append( row )
    
    csv_write( save_path , headers = headers , rows = [ row for cik in sorted( cik_to_rows ) for row in cik_to_rows[ cik ] ] )

    

