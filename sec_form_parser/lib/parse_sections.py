import re
from collections import defaultdict


from utils.utils import *
from utils.text_utils import *
from parse_pages import para_re



section_header0_re = re.compile( '^\s*(item +(?P<item_num>\d+[a-z]?)[\. :]|part +(?P<part_num>i[iv]*)|signatures).*?$' , re.I | re.S )
item_re = re.compile( r'item' , re.I )



def parse_sections( pages , debug = False ) :
    
    for page in pages : page.paras = split_paras( page.text )
    
    matches = [ ]
    
    for i , page in enumerate( pages ) :
        for j , para in enumerate( page.paras ) :
            text = tag_re.sub( '' , para )
            m = section_header0_re.match( text )
            if m and len( list( item_re.finditer( text ) ) ) <= 1 : matches.append( ( m , i , j , para ) )
    
    if debug :
        for m , i , j , para in matches :
            print i , ( pages[ i ].header_page_num , pages[ i ].footer_page_num ) , [ para ]
    
    item_num_to_text_map = defaultdict( str )
    
    for k in range( len( matches ) - 1 ) :
        m1 , i1 , j1 , para1 = matches[ k ]
        m2 , i2 , j2 , para2 = matches[ k + 1 ]
        item_num = m1.group( 'item_num' )
        if item_num :
            item_num = item_num.upper( )
            if i1 == i2 : paras = pages[ i1 ].paras[ j1 + 1 : j2 ]
            else : paras = pages[ i1 ].paras[ j1 + 1 : ] + [ para for page in pages[ i1 + 1 : i2 ] for para in page.paras ] + pages[ i2 ].paras[ : j2 ]
            text = join_paras( paras )
            item_num_to_text_map[ item_num ] = ( item_num_to_text_map[ item_num ] + '\n\n' + text ).strip( '\n' )
            
    return item_num_to_text_map
            