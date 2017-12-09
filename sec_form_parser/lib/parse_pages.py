import re
from collections import Counter


from utils.utils import *
from classes import Page
from pre_parse import page_break_attr_str , table_re , tag_re , num_in_table_str , page_num_str , style_tag_str



page_sep_tag_res = [ re.compile( r'(^|(?<=\n)) *<(page|[^<>]*?(' + page_break_attr_str + r')[^<>]*)> *((?=\n)|$)' , re.I ) ,
                     re.compile( r'(^|(?<=\n)) *<(hr\s[^<>]*)?> *((?=\n)|$)' , re.I ) ]



def parse_pages( text , debug = False ) :
    
    pages = [ ]
    
    for page_sep_tag_re in page_sep_tag_res :
        temp_pages = split_pages( text , page_sep_tag_re )
        if len( temp_pages ) < len( pages ) : continue
        pages = temp_pages
        if len( pages ) > 1 : pages = gather_meta_data( pages )
        if len( pages ) > 20 : break
    
    if debug :
        print '{} pages'.format( len( pages ) ) 
        print [ ( page.header_page_num , page.footer_page_num ) for page in pages if page.header_page_num or page.footer_page_num ]  
    
    return pages



def split_pages( text , page_sep_tag_re ) :
    
    pages = [ ]
    
    segments = split_by_re( text , page_sep_tag_re )    
    for i , segment in enumerate( segments ) :
        segment = segment.strip( '\n' )
        if i % 2 == 0 :
            segment = mend_table( segment )
            segment = discard_tables( segment )
            if i == 0 or segment.strip( ) : pages.append( Page( segment ) )
        else :
            pages[ -1 ].footers.append( segment )    
    
    return pages



table_start_re = re.compile( r'<table(\s[^<>]*)?>.*?((?P<end_tag></table>)|$)' , re.I | re.S )
table_end_re = re.compile( r'^.*?(<table|(?P<end_tag></table>))' , re.I | re.S )



def mend_table( text ) :
    
    ms = list( table_start_re.finditer( text ) )
    if ms and not ms[ -1 ].group( 'end_tag' ) : text += '\n\n</table>'
    
    ms = list( table_end_re.finditer( text ) )
    if ms and ms[ 0 ].group( 'end_tag' ) : text = '<table>\n\n' + text
    
    return text



discardable_table_re = re.compile( r'\s(' + num_in_table_str + r') +(' + num_in_table_str + r')\s|((?<=\n)|^) *(' + num_in_table_str + r'|\$|%|\(|\)) *\n+ *(' + num_in_table_str + r'|\$|%|\(|\)) *?((?=\n)|$)' )



def discard_tables( text ) :
    
    segments = split_by_re( text , table_re )
    for i , segment in enumerate( segments ) :
        if i % 2 == 1 :
            segment = tag_re.sub( '' , segment )
            if len( list( discardable_table_re.finditer( segment ) ) ) > 1 : segments[ i ] = '<table>\n\n...\n\n</table>'
            
    text = ''.join( segments )
    
    return text



line_re = re.compile( r'(^|(?<=\n))( *<table(\s[^<>]*)?>.*?</table> *| *<[^<>]*> *|.*?)((?=\n)|$)' , re.I | re.S )
para_re = re.compile( r'(^|(?<=\n\n))( *<table(\s[^<>]*)?>.*?</table> *|.*?)((?=\n\n)|$)' , re.I | re.S )

#maskable_re = re.compile( r'(^|(?<=\n))[^\n]*?<(?P<tag>small|sub|sup)(\s[^<>]*)?>.*?</(?P=tag)>[^\n]*((?=\n)|$)|</?(' + style_tag_str + r'|table)>' , re.I | re.S )
maskable_re = re.compile( r'</?(' + style_tag_str + r'|table)>' , re.I | re.S )

page_num_text_str = r'\S[^\n<>]*?'

header_footer_re = re.compile( r'^\s*[^\n]*<a>\s*Table\s+of\s+Contents\s*</a>[^\n]*?$|^\s*<(hr\s[^<>]*)?>\s*$' , re.I )

page_num_line_res = [ re.compile( r'^\s*(- *)?(?P<page_num>' + page_num_str + r')( *-)?\s*$' , re.I ) ,
                      re.compile( r'^\s*page +(?P<page_num>' + page_num_str + r')( +of +\d+)?\s*$' , re.I ) ]

texty_page_num_line_res = [ re.compile( r'^\s*(?P<page_num>' + page_num_str + r')\s+(?P<text>' + page_num_text_str + r')\s*$' , re.I ) ,
                            re.compile( r'^\s*(?P<text>' + page_num_text_str + r')\s+(?P<page_num>' + page_num_str + r')\s*$' , re.I ) , 
                            re.compile( r'^\s*page +(?P<page_num>' + page_num_str + r')\s+(?P<text>.*?)\s*$' , re.I | re.S ) , 
                            re.compile( r'^\s*(?P<text>.*?)\s+page +(?P<page_num>' + page_num_str + r')\s*$' , re.I | re.S ) ]

continued_title_re = re.compile( r'\(continued\)|- *continued' , re.I )



def gather_meta_data( pages ) :
    
    
    # gather page numbers, headers and footers
    
    for page in pages : page.lines = [ m.group( ) for m in line_re.finditer( page.text ) ]
    
    for page in pages :
        while page.lines :
            changed = False
            m = header_footer_re.search( page.lines[ -1 ] )
            if m or not maskable_re.sub( '' , page.lines[ -1 ] ).strip( ) :
                page.footers = [ page.lines[ -1 ] ] + page.footers
                page.lines.pop( -1 )
                while page.lines and not page.lines[ -1 ].strip( ) : page.lines.pop( -1 )                                
                continue
            m = header_footer_re.search( page.lines[ 0 ] )
            if m or not maskable_re.sub( '' , page.lines[ 0 ] ).strip( ) :
                page.headers.append( page.lines[ 0 ] )
                page.lines.pop( 0 )
                while page.lines and not page.lines[ 0 ].strip( ) : page.lines.pop( 0 )                                
                continue
            for page_num_line_re in page_num_line_res :
                m = page_num_line_re.search( maskable_re.sub( '' , page.lines[ -1 ] ) )
                if m :
                    page.footers = [ page.lines[ -1 ] ] + page.footers
                    page.lines.pop( -1 )
                    while page.lines and not page.lines[ -1 ].strip( ) : page.lines.pop( -1 )
                    if not page.footer_page_num : page.footer_page_num = m.group( 'page_num' )
                    changed = True
                    break
                m = page_num_line_re.search( maskable_re.sub( '' , page.lines[ 0 ] ) )
                if m :
                    page.headers.append( page.lines[ 0 ] )
                    page.lines.pop( 0 )
                    while page.lines and not page.lines[ 0 ].strip( ) : page.lines.pop( 0 )
                    if not page.header_page_num : page.header_page_num = m.group( 'page_num' )
                    changed = True
                    break
            if changed : continue
            break
    
    text_counter = Counter( ) 
    for page in pages :
        if page.lines :
            for line in ( [ page.lines[ 0 ] ] + [ page.lines[ -1 ] ] if len( page.lines ) > 1 else page.lines ) :
                line = maskable_re.sub( '' , line )
                for page_num_line_re in texty_page_num_line_res :
                    m = page_num_line_re.search( line )
                    if m : text_counter[ ''.join( m.group( 'text' ).lower( ).split( ) ) ] += 1
    
    if text_counter :    
        text , max_count = text_counter.most_common( 1 )[ 0 ]
        valid_texts = [ text for text , count in text_counter.iteritems( ) if count >= ( max_count + 1 ) / 2 > 1 ]        
        for page in pages :
            while page.lines :
                changed = False
                for page_num_line_re in texty_page_num_line_res :
                    m = page_num_line_re.search( maskable_re.sub( '' , page.lines[ -1 ] ) )
                    if m and ''.join( m.group( 'text' ).lower( ).split( ) ) in valid_texts :
                        page.footers = [ page.lines[ -1 ] ] + page.footers
                        page.lines.pop( -1 )
                        while page.lines and not page.lines[ -1 ].strip( ) : page.lines.pop( -1 )
                        if not page.footer_page_num : page.footer_page_num = m.group( 'page_num' )
                        changed = True
                        break
                    m = page_num_line_re.search( maskable_re.sub( '' , page.lines[ 0 ] ) )
                    if m and ''.join( m.group( 'text' ).lower( ).split( ) ) in valid_texts :
                        page.headers.append( page.lines[ 0 ] )
                        page.lines.pop( 0 )
                        while page.lines and not page.lines[ 0 ].strip( ) : page.lines.pop( 0 )
                        if not page.header_page_num : page.header_page_num = m.group( 'page_num' )
                        changed = True
                        break              
                if changed : continue
                break
    
    for page in pages : page.text = '\n'.join( page.lines )
    
    
    # gather titles in headers
    
    for page in pages : page.paras = [ m.group( ) for m in para_re.finditer( page.text ) ]
    
    while True :
    
        text_counter = Counter( )
        for page in pages :
            if page.paras :
                text = ''.join( page.paras[ 0 ].split( ) )
                masked_text = maskable_re.sub( '' , text ).strip( )
                text = text.lower( )
                if text != '<table>...</table>' and masked_text and masked_text[ 0 ].isupper( ) : text_counter[ text ] += 1
        
        if not text_counter : break
        header_titles = [ text for text , count in text_counter.iteritems( ) if count > 1 ]
        if not header_titles : break
        
        for page in pages :
            if page.paras :
                if continued_title_re.search( page.paras[ 0 ] ) or ''.join( page.paras[ 0 ].lower( ).split( ) ) in header_titles :
                    page.headers.append( page.paras[ 0 ] )
                    page.header_title = ( page.header_title + '\n\n' + page.paras[ 0 ] ).strip( '\n' )
                    page.paras.pop( 0 )
                
    for page in pages : page.text = '\n\n'.join( page.paras )
    
    return pages
