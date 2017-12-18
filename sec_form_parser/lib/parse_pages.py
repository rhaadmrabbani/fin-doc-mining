# parse_pages.py
# Author(s): Rhaad M. Rabbani (2017)

# This file contains the page parser.



import re
from collections import Counter



from utils.utils import *
from utils.text_utils import *
from classes import *
from pre_parse import num_in_table_str



############################################
## Functions intended for use by the user ##
############################################



# The page parser extracts pages (represented as page body, header, footer and page number) from the easy-to-read intermediate representation of a document.

def parse_pages( text , debug = False ) :
    
    text = collapse_blocks( text )
    
    segments = [ TextSegment( line ) for line in split_lines( text ) ]
    
    for segment in segments :
        if page_sep_tag_re.match( segment.text ) : segment.is_page_break = True
        if footer_re.match( segment.text ) : segment.is_footer = True
        if header_re.match( segment.text ) : segment.is_header = True
        for page_num_line_re in page_num_line_res :
            m = page_num_line_re.match( segment.tag_masked_text )
            if m : segment.page_num = m.group( 'page_num' ) ; break
    
    # separate pages using footer segments    
    pages = [ Page( ) ]            
    for segment in segments :
        if segment.is_page_break or segment.is_footer :
            pages[ -1 ].footer.append( segment )
            pages.append( Page( ) )
        else :
            pages[ -1 ].text_segments.append( segment )    
    
    build_footers( pages )
    changed = build_footer_page_nums( pages )
    if changed : build_footers( pages )
    
    # remove empty pages
    i = 1
    while i < len( pages ) :
        if not pages[ i ].text_segments and ( not pages[ i - 1 ].footer_page_num or not pages[ i ].footer_page_num ) :
            pages[ i - 1 ].footer_page_num = pages[ i - 1 ].footer_page_num or pages[ i ].footer_page_num
            pages[ i - 1 ].footer += pages[ i ].footer
            pages.pop( i )
            continue
        i += 1
    
    # merge pages across false page seps    
    i = 0
    while i + 1 < len( pages ) :
        if not pages[ i ].footer_page_num and not [ 1 for segment in pages[ i ].footer if segment.is_page_break ] :
            pages[ i + 1 ].text_segments = pages[ i ].text_segments + [ TextSegment( '' ) ] + pages[ i ].footer + [ TextSegment( '' ) ] + pages[ i + 1 ].text_segments
            pages.pop( i )
            continue
        i += 1
        
    build_footers( pages )
    
    while True :
        build_headers( pages )
        changed = build_header_texts( pages )
        if not changed : break
    
    # mend paragraphs broken across page seps
    for page in pages :
        page.text = join_lines( [ segment.text for segment in page.text_segments ] )
        page.text_segments = [ TextSegment( para ) for para in split_paras( page.text ) ]
    i = 0
    while i + 1 < len( pages ) :
        if pages[ i ].text_segments and pages[ i + 1 ].text_segments and broken_para_re.search( pages[ i ].text_segments[ -1 ].text ) :
            pages[ i ].text_segments[ -1 ].text += '\n' + pages[ i + 1 ].text_segments[ 0 ].text
            pages[ i + 1 ].text_segments.pop( 0 )
        i += 1
    
    # remove new lines within paragraphs
    for page in pages :
        for segment in page.text_segments :
            if not non_discardable_block_tag_re.match( segment.text ) : segment.text = junky_nl_re.sub( ' ' , segment.text )
    
    for page in pages : page.text = join_paras( [ segment.text for segment in page.text_segments ] )
    
    if debug :
        print '{} pages'.format( len( pages ) ) 
        print_page_nums( pages )
    
    return pages



page_sep_tag_re = re.compile( r'^\s*(<(page|[^<>]*?(' + page_break_attr_str + r')[^<>]*)>|[^\n]*<a>\s*Table\s+of\s+Contents\s*</a>[^\n]*)\s*$' , re.I )

footer_re = re.compile( r'^\s*(<(hr|!--)(\s[^<>]*)?>|continued\s+on\s+next\s+page)\s*$' , re.I )

header_re = re.compile( r'^\s*(<(hr|!--)(\s[^<>]*)?>|[^\n]*(continued)[^\n]*)\s*$' , re.I )

page_num_line_res = [ re.compile( r'^\s*(- *)?(?P<page_num>' + page_num_str + r')( *-)?\s*$' , re.I ) ,
                      re.compile( r'^\s*page +(?P<page_num>' + page_num_str + r')( +of +\d+)?\s*$' , re.I ) ]

non_discardable_block_tag_re = re.compile( r'(^|(?<=\n))\s*<(?P<tag>' + non_discardable_block_tag_str + r')(\s[^<>]*)?>.*?</(?P=tag)>\s*((?=\n)|$)' , re.I | re.S )

broken_para_re = re.compile( r'[^\.>\s\'"][\s\'"]*$' )



#######################################################
## Helper functions not intended for use by the user ##
#######################################################



def collapse_blocks( text ) :
    
    segments = split_by_re( text , non_discardable_block_tag_re )
    for i , segment in enumerate( segments ) :
        if i % 2 == 1 :
            tag = non_discardable_block_tag_re.match( segment ).group( 'tag' )
            segment = tag_re.sub( '' , segment )
            if len( list( collapsable_block_re.finditer( segment ) ) ) > 1 : segments[ i ] = '\n\n<{0}>\n\n...\n\n</{0}>\n\n'.format( tag )
            
    text = ''.join( segments )
    
    return text



def build_footers( pages ) :  
    
    for page in pages :
        while page.text_segments :
            if not page.text_segments[ -1 ].text.strip( ) :
                page.text_segments.pop( -1 )
            elif page.text_segments[ -1 ].is_footer :
                page.footer = [ page.text_segments[ -1 ] ] + page.footer
                page.text_segments.pop( -1 )
            elif not page.footer_page_num and page.text_segments[ -1 ].page_num :
                page.footer_page_num = page.text_segments[ -1 ].page_num
                page.footer = [ page.text_segments[ -1 ] ] + page.footer
                page.text_segments.pop( -1 )
            else :
                break



def build_headers( pages ) :
    
    for page in pages :
        while page.text_segments :
            if not page.text_segments[ 0 ].text.strip( ) :
                page.text_segments.pop( 0 )
            elif page.text_segments[ 0 ].is_header :
                page.header = page.header + [ page.text_segments[ 0 ] ]
                page.text_segments.pop( 0 )
            elif not page.header_page_num and page.text_segments[ 0 ].page_num :
                page.header_page_num = page.text_segments[ 0 ].page_num
                page.header = page.header + [ page.text_segments[ 0 ] ]
                page.text_segments.pop( 0 )
            else :
                break



def build_footer_page_nums( pages ) :
    
    text_counter = Counter( ) 
    
    for page in pages :
        if not page.footer_page_num and page.text_segments :
            page.text_segments[ -1 ].temp_page_num = ''
            page.text_segments[ -1 ].temp_page_num_text = ''            
            for page_num_line_re in texty_page_num_line_res :
                m = page_num_line_re.match( page.text_segments[ -1 ].tag_masked_text )
                if m :
                    page.text_segments[ -1 ].temp_page_num = m.group( 'page_num' )
                    page.text_segments[ -1 ].temp_page_num_text = ''.join( m.group( 'text' ).lower( ).split( ) )
                    text_counter[ page.text_segments[ -1 ].temp_page_num_text ] += 1
                    break
    
    if not text_counter : return pages    
    
    text , max_count = text_counter.most_common( 1 )[ 0 ]
    valid_texts = [ text for text , count in text_counter.iteritems( ) if count >= ( max_count + 1 ) / 2 > 1 ] 

    for page in pages :
        if not page.footer_page_num and page.text_segments and page.text_segments[ -1 ].temp_page_num and page.text_segments[ -1 ].temp_page_num_text in valid_texts :
            page.footer_page_num = page.text_segments[ -1 ].temp_page_num
            page.footer = [ page.text_segments[ -1 ] ] + page.footer
            page.text_segments.pop( -1 )                    



def build_header_texts( pages ) :
    
    changed = False
    
    text_counter = Counter( ) 
    
    for page in pages :
        if page.text_segments :
            text_counter[ ''.join( page.text_segments[ 0 ].text.lower( ).split( ) ) ] += 1
            
    valid_texts = [ text for text , count in text_counter.iteritems( ) if count > 1 ] 
    
    for page in pages :
        if page.text_segments :
            if ''.join( page.text_segments[ 0 ].text.lower( ).split( ) ) in valid_texts :
                page.header = page.header + [ page.text_segments[ 0 ] ]
                page.text_segments.pop( 0 )
                changed = True
    
    return changed



def page_num_adjacency_check( ( header_page_num0 , footer_page_num0 ) , ( header_page_num1 , footer_page_num1 ) ) :
    
    if not header_page_num0 and not header_page_num1 and footer_page_num0 and footer_page_num1 :
        m0 = page_num_re.match( footer_page_num0 )
        m1 = page_num_re.match( footer_page_num1 )
        return m0.group( 'pre' ) == m1.group( 'pre' ) and int( m0.group( 'num' ) ) + 1 == int( m1.group( 'num' ) )
    
    if header_page_num0 and header_page_num1 and not footer_page_num0 and not footer_page_num1 :
        m0 = page_num_re.match( header_page_num0 )
        m1 = page_num_re.match( header_page_num1 )
        return m0.group( 'pre' ) == m1.group( 'pre' ) and int( m0.group( 'num' ) ) + 1 == int( m1.group( 'num' ) )    

    if header_page_num0 and header_page_num1 and footer_page_num0 and footer_page_num1 :
        mh0 = page_num_re.match( header_page_num0 )
        mh1 = page_num_re.match( header_page_num1 )
        mf0 = page_num_re.match( footer_page_num0 )
        mf1 = page_num_re.match( footer_page_num1 )        
        return mh0.group( 'pre' ) == mh1.group( 'pre' ) and int( mh0.group( 'num' ) ) + 1 == int( mh1.group( 'num' ) ) \
               and mf0.group( 'pre' ) == mf1.group( 'pre' ) and int( mf0.group( 'num' ) ) + 1 == int( mf1.group( 'num' ) ) 

    return False


def print_page_nums( pages ) :
    
    page_nums = [ ( page.header_page_num , page.footer_page_num ) for page in pages if page.header_page_num or page.footer_page_num ]    
    groups = group_items( page_nums , page_num_adjacency_check )
    print 'numbered pages: [' + '; '.join( [ 'from {} to {}'.format( group[ 0 ] , group[ -1 ] )for group in groups ] ) + ']'



collapsable_block_re = re.compile( r'\s(' + num_in_table_str + r')\s+(-+\s+)?(' + num_in_table_str + r')\s|\s(\d+\s+){3}' )

texty_page_num_line_res = [ re.compile( r'^\s*(page +)?(?P<page_num>' + page_num_str + r')\s+(?P<text>.*?)\s*$' , re.I | re.S ) , 
                            re.compile( r'^\s*(?P<text>.*?)\s+(page +)?(?P<page_num>' + page_num_str + r')\s*$' , re.I | re.S ) ]

page_num_re = re.compile( r'^(?P<pre>.*?)(?P<num>\d+)$' )



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
