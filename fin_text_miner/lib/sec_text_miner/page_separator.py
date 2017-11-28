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


from html_parser import page_attr_str , page_attr_re


num_str = r'[\divx]{1,3}'

start_tag_re = re.compile( r'<(?P<tag>[a-z]\S*)[^<>]*>' , re.I )

end_tag_re = re.compile( r'</(?P<tag>\S+)>' , re.I )

page_num_re = re.compile( r'^((?P<pre>[A-Z]{1,3}) *-? *)??(?P<num>' + num_str + ')$' , re.I )


class PageSep :
    
    def __init__( self , match_obj , text ) :
        self.start = match_obj.start( )
        self.end = match_obj.end( )
        self.page_nums = [ ]
        self.texts = set( [ ' '.join( match_obj.group( 'text' ).lower( ).split( ) ) ] if match_obj.group( 'text' ) else [ ] )
        matched_text = text[ match_obj.start( ) : match_obj.end( ) ]
        self.tags = set( [ m.group( 'tag' ).lower( ) for m in start_tag_re.finditer( matched_text ) ] )
        self.page_tagged = True if page_attr_re.search( matched_text ) or 'page' in self.tags else False
        page_num = match_obj.group( 'page_num' )
        if page_num :
            m = page_num_re.match( page_num )
            pre = ( m.group( 'pre' ) or '' ).upper( )
            num = m.group( 'num' ).lower( )
            if num.isdigit( ) : num = int( num )
            self.page_nums = [ ( pre , num ) ]
            
    def __lt__( self , other ) :
        return ( self.start , -self.end ) < ( other.start , -other.end )
        
    def merge( self , other ) :
        self.end = other.end
        self.page_nums += other.page_nums
        self.texts |= other.texts
        self.tags |= other.tags
        
    def has_page_num_immediately_before( self , other ) :
        if len( self.page_nums ) == len( other.page_nums ) :
            good = True
            for j in range( len( self.page_nums ) ) :
                if self.page_nums[ j ][ 0 ] != other.page_nums[ j ][ 0 ] \
                   or not type( self.page_nums[ j ][ 1 ] ) is int or not type( other.page_nums[ j ][ 1 ] ) is int \
                   or other.page_nums[ j ][ 1 ] - self.page_nums[ j ][ 1 ] != 1 :
                    good = False
                    break
            if good : return True
        return False


bad_page_num_re = re.compile( '^EX-|^[A-Z]*$' , re.I )

bad_page_sep_text_re = re.compile( r'^\s*(part|table|schedule|basel)\s*$|[<>]' , re.I )


class PageSepGenerator :
    
    def __init__( self , masked_text , text , regexp ) :
        self.masked_text = masked_text
        self.text = text
        self.regexp = regexp
        
    def generate_objs( self ) :
        return [ PageSep( match_obj , self.text ) for match_obj in self.regexp.finditer( self.masked_text )
                 if ( not match_obj.group( 'page_num' ) or not bad_page_num_re.search( match_obj.group( 'page_num' ) ) )
                 and ( not match_obj.group( 'text' ) or not bad_page_sep_text_re.search( match_obj.group( 'text' ) ) ) ]


page_sep_res = { }

page_sep_res[ 00 ] = re.compile( r'(?P<page_num>)(?P<text>)<hr( [^<>]*)?>' , re.I )
page_sep_res[ 01 ] = re.compile( r'((?<=\n)|^)(?P<page_num>)(?P<text>)[^\n]*<a>\s*Table\s+of\s+Contents\s*</a>[^\n]*((?=\n)|$)' , re.I )

to_mask_re = re.compile( r'((?<=\n)|^)[^\n]*?<(?P<tag>small|sub|sup)(\s[^<>]*)?>.*?</(?P=tag)>[^\n]*((?=\n)|$)|<[^<>]*>' , re.I | re.S )
skip_mask_re = re.compile( r'<(/?table|hr)(\s[^<>]*)?>|<page>|<[^<>]*?(' + page_attr_str + r')[^<>]*>' , re.I )

page_sep_res[ 10 ] = re.compile( r'((?<=\n)|^)(?P<text>) *<page> *(?P<page_num>' + num_str + ')?\s*?((?=\n)|$)' , re.I )
page_sep_res[ 11 ] = re.compile( r'(?P<page_num>)(?P<text>)<[^<>]*?(' + page_attr_str + r')[^<>]*>' , re.I )
page_sep_res[ 12 ] = re.compile( r'<table(\s[^<>]*)?>\s*((?P<text>page) +)?(- *)?(?P<page_num>([A-Z]{1,3} *-? *)??' + num_str + ')( *-)?( +of +\d{1,3})?\s*</table>' , re.I )
page_sep_res[ 13 ] = re.compile( r'<table(\s[^<>]*)?>\s*(?P<page_num>' + num_str + ')\s+(?P<text>\S[^\n<>]*?)\s*</table>' , re.I )
page_sep_res[ 14 ] = re.compile( r'<table(\s[^<>]*)?>\s*(?P<text>\S[^\n<>]*?)\s+(?P<page_num>' + num_str + ')\s*</table>' , re.I )

table_re = re.compile( r'<table( [^<>]*)?>.*?</table>' , re.I | re.S )

page_sep_res[ 20 ] = re.compile( r'((?<=\n)|^) *((?P<text>page) +)?(- *)?(?P<page_num>([A-Z]{1,3} *-? *)??' + num_str + ')( *-)?( +of +\d{1,3})?\s*?((?=\n)|$)' , re.I )
page_sep_res[ 21 ] = re.compile( r'((?<=\n)|^) *\r?\n *(?P<page_num>' + num_str + ') +(?P<text>\S[^\n<>]*?)\s*?\n\s*?((?=\n)|$)' , re.I )
page_sep_res[ 22 ] = re.compile( r'((?<=\n)|^) *\r?\n *(?P<text>\S[^\n<>]*?) +(?P<page_num>' + num_str + ')\s*?\n\s*?((?=\n)|$)' , re.I )

def get_default_page_sep_generators( text ) :
    
    page_sep_generators = [ ]
    
    page_sep_generators.append( PageSepGenerator( text , text , page_sep_res[ 00 ] ) )
    page_sep_generators.append( PageSepGenerator( text , text , page_sep_res[ 01 ] ) )
    
    masked_text = to_mask_re.sub( lambda m : m.group( ) if skip_mask_re.match( m.group( ) ) else ' ' * len( m.group( ) ) , text )
    
    page_sep_generators.append( PageSepGenerator( masked_text , text , page_sep_res[ 10 ] ) )
    page_sep_generators.append( PageSepGenerator( masked_text , text , page_sep_res[ 11 ] ) )
    page_sep_generators.append( PageSepGenerator( masked_text , text , page_sep_res[ 12 ] ) )
    page_sep_generators.append( PageSepGenerator( masked_text , text , page_sep_res[ 13 ] ) )
    page_sep_generators.append( PageSepGenerator( masked_text , text , page_sep_res[ 14 ] ) )    

    table_masked_text = table_re.sub( lambda m : ' ' * len( m.group( ) ) , masked_text )
    
    page_sep_generators.append( PageSepGenerator( table_masked_text , text , page_sep_res[ 20 ] ) )
    page_sep_generators.append( PageSepGenerator( table_masked_text , text , page_sep_res[ 21 ] ) )
    page_sep_generators.append( PageSepGenerator( table_masked_text , text , page_sep_res[ 22 ] ) )
    
    return page_sep_generators
    
    
def separate_pages( text , page_sep_generators , debug = False ) :
    
    page_seps = [ page_sep for g in page_sep_generators for page_sep in g.generate_objs( ) ]
    
    page_seps = remove_easy_false_positives( page_seps )
    page_seps.sort( )    
    page_seps = remove_overlapped_page_seps( page_seps )
    page_seps = grow_page_seps( text , page_seps )
    
    if debug : print [ page_sep.page_nums for page_sep in page_seps ]
    
    page_seps = remove_hard_false_positives( page_seps , debug )
    
    if debug : print [ page_sep.page_nums for page_sep in page_seps ]
    
    pages = form_pages( text , page_seps )
    
    return pages


# HELPER FUNCTION(S)


def remove_easy_false_positives( page_seps ) :
    
    texts = [ list( page_sep.texts )[ 0 ] for page_sep in page_seps if page_sep.texts ]
    counter = Counter( texts )
    texts = [ text for text in counter if counter[ text ] >= 3 ]
    
    page_seps = [ page_sep for page_sep in page_seps if not page_sep.texts or list( page_sep.texts )[ 0 ] in texts ]
    
    return page_seps


def remove_overlapped_page_seps( page_seps ) :

    for i in range( len( page_seps ) - 1 ) :
        if page_seps[ i ].end >= page_seps[ i + 1 ].start :
            page_seps[ i : i + 2 ] = [ None , page_seps[ i ] ]

    page_seps = [ page_sep for page_sep in page_seps if page_sep ]
    
    return page_seps


just_tags_re = re.compile( r'^\s*(<[^<>]*>\s*)*$' )


def grow_page_seps( text , page_seps ) :
    
    changed = True
    
    while ( changed ) :
        
        changed = False
    
        # merge
        for i in range( len( page_seps ) - 1 ) :
            page = text[ page_seps[ i ].end : page_seps[ i + 1 ].start ]
            if just_tags_re.match( page ) :
                page_seps[ i ].merge( page_seps[ i + 1 ] )
                page_seps[ i : i + 2 ] = [ None , page_seps[ i ] ]
                changed = True        
        page_seps = [ page_sep for page_sep in page_seps if page_sep ]
        
        for i in range( len( page_seps ) ) :
            # include end tags below page_sep with matching start tags in page_sep
            page_end = len( text ) if i == len( page_seps ) - 1 else page_seps[ i + 1 ].start
            page = text[ page_seps[ i ].end : page_end ]
            while True :
                page = page.split( '\n' , 1 )
                if len( page ) == 1 : break
                if not page[ 0 ].strip( ) :
                    page = page[ -1 ]
                    continue
                if start_tag_re.search( page[ 0 ] ) : break
                m = end_tag_re.search( page[ 0 ] )
                if m and m.group( 'tag' ).lower( ) in page_seps[ i ].tags :
                    page_seps[ i ].end = page_end - len( page[ -1 ] ) - 1 - ( len( page[ 0 ] ) - m.end( ) )
                    page = page[ 0 ][ m.end( ) : ] + '\n' + page[ -1 ] 
                    changed = True                    
                    continue
                else : break
    
    return page_seps


def remove_hard_false_positives( page_seps , debug ) :
    
    groups = [ ]
    
    i = 0
    while i < len( page_seps ) :
        if page_seps[ i ].page_nums :
            groups = [ [ page_seps[ i ] ] ]
            i += 1
            break
        i += 1
    
    to_remove = set( )
    
    while i < len( page_seps ) :
        if page_seps[ i ].page_nums :
            for j in range( len( groups ) )[ : : -1 ] :
                if groups[ j ][ -1 ].has_page_num_immediately_before( page_seps[ i ] ) :
                    if not groups[ j ][ -1 ].tags and not page_seps[ i ].tags and not groups[ j ][ -1 ].page_tagged and not page_seps[ i ].page_tagged and not groups[ j ][ -1 ].texts and not page_seps[ i ].texts \
                       or groups[ j ][ -1 ].tags | page_seps[ i ].tags \
                       or groups[ j ][ -1 ].page_tagged and page_seps[ i ].page_tagged \
                       or groups[ j ][ -1 ].texts | page_seps[ i ].texts \
                       or 'page' in groups[ j ][ -1 ].texts | page_seps[ i ].texts :
                        groups[ j ].append( page_seps[ i ] )
                        to_remove |= set( [ page_sep for g in groups[ j + 1 : ] for page_sep in g ] )
                        groups[ j + 1 : ] = [ ]
                    else :
                        groups.append( [ page_seps[ i ] ] )
                    break
                elif j == 0 or groups[ j ][ -1 ].page_tagged or 'page' in groups[ j ][ -1 ].texts :
                    groups.append( [ page_seps[ i ] ] )
                    break
        i += 1
    
    if debug : print [ str( g[ 0 ].page_nums ) + ' to ' + str( g[ -1 ].page_nums ) if len( g ) > 1 else str( g[ 0 ].page_nums ) for g in groups ]
    
    page_seps = sorted( set( page_seps ) - to_remove )
    
    return page_seps


def form_pages( text , page_seps ) :
    
    if not page_seps : return [ text ]
    
    ms = [ ( page_sep.start , page_sep.end ) for page_sep in page_seps ]
    non_ms = [ ( 0 , page_seps[ 0 ].start ) ] \
               + zip( [ page_sep.end for page_sep in page_seps[ : -1 ] ] , [ page_sep.start for page_sep in page_seps[ 1 : ] ] ) \
               + [ ( page_seps[ -1 ].end , len( text ) ) ]
    
    all_ms = [ non_ms[ 0 ] ] + [ m for m_pair in zip( *[ ms , non_ms[ 1 : ] ] ) for m in m_pair ]
    pages = [ text[ m[ 0 ] : m[ -1 ] ].strip( ) for m in all_ms ]
    
    return pages
