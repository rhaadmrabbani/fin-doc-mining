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
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,  OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import re


class SectionHdr :
    
    def __init__( self , match_obj , text ) :
        self.start = match_obj.start( )
        self.end = match_obj.end( )
        self.section_num = match_obj.group( 'section_num' )


class SectionHdrGenerator :
    
    def __init__( self , masked_text , text , regexp ) :
        self.masked_text = masked_text
        self.text = text
        self.regexp = regexp
        
    def generate_objs( self ) :
        return [ SectionHdr( match_obj , self.text ) for match_obj in self.regexp.finditer( self.masked_text ) ]


section_hdr_res = { }

section_hdr_res[ 00 ] = re.compile( r'((?<=\n)|^) *(item +(?P<section_num>\d\S*?)\.?( |[A-Z]{2}).*?|signatures *)((?=\n\s*\n)|$)' , re.I | re.S )


def get_default_section_hdr_generators( text ) :
    
    section_hdr_generators = [ ]
    
    section_hdr_generators.append( SectionHdrGenerator( text , text , section_hdr_res[ 00 ] ) )
    
    return section_hdr_generators


def separate_sections( text , section_hdr_generators , debug = False ) :
    
    section_hdrs = [ section_hdr for g in section_hdr_generators for section_hdr in g.generate_objs( ) ]
    
    if debug :
        for section_hdr in section_hdrs :
            print [ section_hdr.section_num , text[ section_hdr.start : section_hdr.end ] ]
    
    