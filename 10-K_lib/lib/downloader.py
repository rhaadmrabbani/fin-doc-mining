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


import os
import re
import urllib2


from utils import load_text , save_text , load_csv , save_csv


# download raw content from url			

def download( url , debug = False ) :
    
    if debug : print 'Downloading ' + url + ' ...'
        
    response = urllib2.urlopen( url )
    raw = response.read( )
    
    return raw

folder_re = re.compile( r'<a href="(?P<folder>\w+)/"><img [^>]*? alt="folder icon">' , re.I | re.S )

index_junk_re = re.compile( r'^.*?(\r?\n *){3,}|(?<=\n)-+\r?\n' , re.S )

nl_re = re.compile( r'\r?\n' )


# download and save all quarterly indexes available at SEC's online archive as csv files

def download_and_save_indexes( save_dir ) :

    raw = download( 'https://www.sec.gov/Archives/edgar/full-index/' )
    
    for m in folder_re.finditer( raw ) :
        
        year = m.group( 'folder' )        
        raw = download( 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/' )
        
        for m in folder_re.finditer( raw ) :
    
            qtr = m.group( 'folder' )
            save_path = save_dir + '/' + year + '_' + qtr + '.csv'            
            if os.path.isfile( save_path ) : continue
      
            idx = download( 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/' + qtr + '/master.idx' , debug = True )
            idx = index_junk_re.sub( '' , idx )
            rows = [ line.split( '|' ) for line in nl_re.split( idx ) if line ]
            save_csv( save_path , rows = rows )
			

div_re = re.compile( r'<tr[^>]*>\s*(<td[^>]*>[^<]*</td>\s*){2}<td[^>]*><a href="(?P<rel_url>[^"]*\.txt)">\s*[^\s<]+\s*</a></td>\s*<td[^>]*>(?P<doc_type>10-K|EX-13[^<]*)</td>' )

doc_re = re.compile( r'<document>(?P<doc>.*?)</document>' , re.I | re.S )

doc_type_re = re.compile( r'<type>(?P<type>.*?)\n' , re.I )

doc_text_re = re.compile( r'<text>(?P<text>.*?)</text>' , re.I | re.S )

doc_pdf_re = re.compile( r'<pdf>.*?</pdf>' , re.I | re.S )


# download 10-K and EX-13x docs, given relative url of txt file containing all 10-K related docs,
# and return dictionary containing map from document type to text

def download_10K_docs( rel_url ) :
    
    docs = { }
    
    raw = download( 'https://www.sec.gov/Archives/' + rel_url[ : -4 ] + '-index.htm' )
    div_ms = list( div_re.finditer( raw ) )
    
    if div_ms :
	
        for m in div_ms :
            url = 'https://www.sec.gov' + m.group( 'rel_url' )
            if url.lower( ).endswith( '.pdf' ) : continue
            doc = download( url , debug = True )
            doc_type = m.group( 'doc_type' )
            doc_text = doc_text_re.search( doc ).group( 'text' )
            docs[ doc_type ] = doc_text
			
    else :
		
        raw = download( 'https://www.sec.gov/Archives/' + rel_url , debug = True )
        for doc_m in doc_re.finditer( raw ) :
            doc = doc_m.group( 'doc' )
            doc_type = doc_type_re.search( doc ).group( 'type' ).strip( )    
            if not ( doc_type == '10-K' or doc_type.startswith( 'EX-13' ) ) : continue
            doc_text = doc_text_re.search( doc ).group( 'text' )
            if doc_pdf_re.search( doc_text ) : continue
            docs[ doc_type ] = doc_text
    
    return docs
        
			
			

