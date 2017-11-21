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


import os , os.path
import csv


def csv_read( load_path , headers ) :
    
    rows = [ ]
    
    load_file = open( load_path , 'rb' )
    
    for row in csv.DictReader( load_file ) :
        row = [ row[ header ] for header in headers ]
        rows.append( row )
    
    load_file.close( )
    
    return rows


def csv_write( save_path , headers = None , rows = None ) :
    
    save_dir = os.path.dirname( save_path )    
    if save_dir and not os.path.isdir( save_dir ) : os.makedirs( save_dir )
    
    save_file = open( save_path , 'wb' )
    csv_writer = csv.writer( save_file , delimiter = ',' , quotechar = '"' , quoting = csv.QUOTE_MINIMAL )
    
    if headers :
        csv_writer.writerow( headers )
    if rows :
        for row in rows :
            csv_writer.writerow( row )
    
    save_file.close( )
    