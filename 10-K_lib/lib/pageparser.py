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
from collections import Counter


from htmlparser import page_attr_str


class Page_Sep :
    def __init__( self , m = None , page_num = None , non_num = None ) :
        if m : self.ms = [ m ]
        self.page_nums = [ ] + ( [ page_num ] if page_num else [ ] )
        self.non_num = non_num
    def group( self ) :
        return '\n\n'.join( [ m.group( ) for m in self.ms ] )
    def start( self ) :
        return self.ms[ 0 ].start( )
    def end( self ) :
        return self.ms[ -1 ].end( )
    def __repr__( self ) :
        return ' , '.join( self.page_nums )  


page_num_str_simple = r'\d{1,3}'
    
page_num_str = r'(page +)?((- *)?\d{1,3}\.?( *-)?|[A-Z]{1,3} *-? *\d{1,3})( +of +\d{1,3})?'
    
page_sep_str = r'<page>( *(?P<num>' + page_num_str + r') *)?|<[^<>]*?(' + page_attr_str + ')[^<>]*>'


to_mask_re = re.compile( r'<(?P<tag>small|sub|sup)( [^<>]*)?>.*?</(?P=tag)>|<[^<>]*>' , re.I | re.S )

skip_mask_re = re.compile( r'<(/?table|hr)( [^<>]*)?>|' + page_sep_str , re.I )

page_sep_re_masked = re.compile( page_sep_str , re.I )

page_sep_re = re.compile( r'((?<=\n)|^)[^\n]*<a>\s*Table\s+of\s+Contents\s*</a>[^\n]*((?=\n)|$)' , re.I )

table_re = re.compile( r'<table( [^<>]*)?>.*?</table>' , re.I | re.S )

page_num_re_table_masked = re.compile( r'((?<=\n)|^) *(?P<num>' + page_num_str + r')\s*?((?=\n)|$)' , re.I )

page_num_re_masked = re.compile( r'<table>\s*(?P<num>' + page_num_str + r')\s*</table>' , re.I )

page_num_re_masked_maybes = [ re.compile( r'<table>\s*(?P<num>' + page_num_str_simple + r')\s+(?P<non_num>\S+?[^\n]*\S+)\s*</table>' , re.I ) ,
                              re.compile( r'<table>\s*(?P<non_num>\S+?[^\n]*\S+)\s+(?P<num>' + page_num_str_simple + r')\s*</table>' , re.I ) ]

page_num_re_table_masked_maybes = [ re.compile( r'((?<=\n)|^)\s*\n *(?P<num>' + page_num_str_simple 
                                                + r') +(?P<non_num>\S+?[^\n]*\S+)\s*\n\s*((?=\n)|$)' , re.I ) ,
                                    re.compile( r'((?<=\n)|^)\s*\n *(?P<non_num>\S+?[^\n]*\S+) +(?P<num>' + page_num_str_simple
                                                + r')\s*\n\s*((?=\n)|$)' , re.I ) ]

not_page_re = re.compile( r'^\s*(<[^<>]*>\s*)*$' )

any_re = re.compile( '(.*)' )


# split text into list where every even-indexed string is a page, and every odd-indexed string is a page sep

def split_to_pages( text , debug = False ) :
	
    page_seps = [ ]
    
    masked_text = to_mask_re.sub( lambda m : m.group( ) if skip_mask_re.match( m.group( ) ) else ' ' * len( m.group( ) ) , text )
    table_masked_text = table_re.sub( lambda m : ' ' * len( m.group( ) ) , masked_text )
    
    page_seps += [ Page_Sep( page_sep , page_num = page_sep.group( 'num' )  ) for page_sep in page_sep_re_masked.finditer( masked_text ) ]    
    page_seps += [ Page_Sep( page_sep ) for page_sep in page_sep_re.finditer( text ) ]    
    page_seps += [ Page_Sep( page_sep , page_num = page_sep.group( 'num' ) ) for page_sep in page_num_re_table_masked.finditer( table_masked_text ) ]    
    page_seps += [ Page_Sep( page_sep , page_num = page_sep.group( 'num' ) ) for page_sep in page_num_re_masked.finditer( masked_text ) ]
    
    for masked_maybe_text , page_num_re_maybe in [ ( masked_text , r ) for r in page_num_re_masked_maybes ] \
                                                 + [ ( table_masked_text , r ) for r in page_num_re_table_masked_maybes ] :
        temp_page_seps = [ Page_Sep( page_sep , page_num = page_sep.group( 'num' ) ) for page_sep in page_num_re_maybe.finditer( masked_maybe_text ) ]
        if temp_page_seps :
            non_num_counter = Counter( [ page_sep.non_num for page_sep in temp_page_seps ] )
            non_num , count = non_num_counter.most_common( 1 )[ 0 ]
            if count >= 3 : page_seps += [ page_sep for page_sep in temp_page_seps if page_sep.non_num == non_num ]
    
    page_seps.sort( key = lambda m : ( m.start( ) , - m.end( ) ) )    
    page_seps = reduce_page_seps( page_seps , text )

    #temp page seps
    # hr if none or next to seps
    # num + name make set of name and see if size 2
    
    if debug == True : print [ str( page_sep ) for page_sep in page_seps ]
        
    pages = form_pages( text , page_seps )
        
    return pages


# filter out any page_sep that is completely overlapped by a longer page_sep        
# merge adjacent page_seps

def reduce_page_seps( page_seps , text ) :
    
    # remove overlapped
    for i in range( len( page_seps ) - 1 ) :
        if page_seps[ i ].end( ) >= page_seps[ i + 1 ].start( ) :
            page_seps[ i : i + 2 ] = [ None , page_seps[ i ] ]
    
    page_seps = [ page_sep for page_sep in page_seps if page_sep ]    
    
    # merge
    for i in range( len( page_seps ) - 1 ) :
        middle = text[ page_seps[ i ].end( ) : page_seps[ i + 1 ].start( ) ]
        if not_page_re.match( middle ) :
            page_seps[ i ].page_nums += page_seps[ i + 1 ].page_nums
            page_seps[ i ].ms += page_seps[ i ].ms + any_re.findall( '\n\n' + middle + '\n\n' if middle.strip( ) else middle ) + page_seps[ i + 1 ].ms
            page_seps[ i : i + 2 ] = [ None , page_seps[ i ] ]
    
    page_seps = [ page_sep for page_sep in page_seps if page_sep ] 
    
    return page_seps


def form_pages( text , page_seps ) :
    
    if not page_seps : return [ text ]
    
    ms = [ ( m.start( ) , m.end() ) for m in page_seps ]
    non_ms = [ ( 0 , ms[ 0 ][ 0 ] ) ] \
               + zip( [ m[ -1 ] for m in ms[ : -1 ] ] , [ m[ 0 ] for m in ms[ 1 : ] ] ) \
               + [ ( ms[ -1 ][ -1 ] , len( text ) ) ]
    
    all_ms = [ non_ms[ 0 ] ] + [ m for m_pair in zip( *[ ms , non_ms[ 1 : ] ] ) for m in m_pair ]
    pages = [ text[ m[ 0 ] : m[ -1 ] ].strip( ) for m in all_ms ]
    
    return pages


    