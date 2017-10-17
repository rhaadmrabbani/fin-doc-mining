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


import re


doc_re = re.compile( r'<document>(?P<doc>.*?)</document>' , re.I | re.S )

doc_type_re = re.compile( r'<type>(?P<type>.*?)\n' , re.I )

doc_text_re = re.compile( r'<text>(?P<text>.*?)</text>' , re.I | re.S )

doc_pdf_re = re.compile( r'<pdf>.*?</pdf>' , re.I | re.S )


def get_docs( load_path , doc_types ) :
    
    doc_types = set( doc_types )
    
    load_file = open( load_path )
    text = load_file.read( )
    load_file.close( )
    
    docs = [ ]
    
    for doc_m in doc_re.finditer( text ) :
        
        doc = doc_m.group( 'doc' )
        
        doc_type = doc_type_re.search( doc ).group( 'type' ).strip( )    
        if not doc_type in doc_types : continue
        
        doc_text = doc_text_re.search( doc ).group( 'text' )    
        if doc_pdf_re.search( doc_text ) : continue
        
        docs.append( ( doc_type , doc_text ) )
    
    return docs
