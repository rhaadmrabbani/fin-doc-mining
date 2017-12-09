import re
import sys


from utils.utils import *
from classes import HtmlNode



is_html_re = re.compile( r'<(div|html|p|title)(\s[^<>*])?>|<!doctype>\s[^<>]*html' , re.I )

tab_re = re.compile( r'\t' )
cr_re = re.compile( r'\r' )
multi_nl_re = re.compile( r'\n\s*\n' )



def pre_parse( text ) :
    
    text = tab_re.sub( ' ' , text )
    text = cr_re.sub( '' , text )
    text = multi_nl_re.sub( '\n\n' , text )
    text = text.strip( '\n' ) + '\n'
    
    text = ( pre_parse_html if is_html_re.search( text ) else pre_parse_non_html )( text )  
    
    return text



special_char_re = re.compile( r'&(?P<code>.{1,6}?);' , re.S )
special_char_map = dict( [ ( k , v ) for ks , v in [ ( [ 'nbsp' , '#160' , '#9' ] , ' ' ) , ( [ 'amp' , '#38' ] , '&' ) , ( [ '#43' ] , ' + ' ) , ( [ 'lt' , '#60' ] , '<' ) , ( [ 'gt' , '#62' ] , '>' ) ,
                                                     ( [ '#91' ] , ' [ ' ) , ( [ '#93' ] , ' ] ' ) , ( [ '#95' ] , '_' ) , ( [ '&rsquo' , '#145' , '#146' , '#8216' , '#8217' ] , "'" ) ,
                                                     ( [ '&ldquo' , '&rdquo' ,  'quot' , '#147' , '#148' , '#8220' , '#8221' ] , '"' ) , ( [ '#150' , '#151' , '#8212' ] , ' - ' ) ] for k in ks ] )

def special_char_sub( m ) :    
    code = m.group( 'code' )
    if code.startswith( '#' ) :
        if code[ 1 : ].startswith( 'x' ) and code[ 2 : ].isdigit( ) : code = '#' + str( int( code[ 2 : ] ) ) # hex to dec
        elif code[ 1 : ].isdigit( ) : code = '#' + str( int( code[ 1 : ] ) ) # remove leading zeros
    sub = special_char_map[ code ] if code in special_char_map else ' '
    return sub 



tag_re = re.compile( r'(<(?P<tag>/?[!a-z]\w*)(?P<attrs>[^<>]*)>)' , re.I )
junk_nl_re = re.compile( r'\s*\n\s*' )

page_break_attr_str = r'page[^<>]*break|(?<=[^a-z])pg[^<>]*brk'
non_discardable_block_tag_str = r'dir|dl|ol|pre|table|ul'

childless_tag_re = re.compile( r'^(!--|br|hr|page)$' , re.I )



def pre_parse_html( text ) :
    
    html_tree = get_html_tree( text )
    text = get_interm_repr( html_tree )   
    
    return text



non_nestable_tag_re = re.compile( r'^(' + non_discardable_block_tag_str + r'body|head|html|title|p)$' , re.I )



def get_html_tree( text ) :

    # every even numbered segment is not a tag, every odd numbered segment is a tag
    segments = split_by_re( text , tag_re )
    
    # create root node
    node = HtmlNode( None , 'html' , '' )
    html_tree = node
    
    for i , segment in enumerate( segments ) :
        
        if not node : break
        
        if i % 2 == 0 or node.tag == 'pre' and segment != '</pre>' :
            
            segment = special_char_re.sub( special_char_sub , segment )
            if node.tag != 'pre' : segment = junk_nl_re.sub( ' ' , segment )
            node.children.append( segment )
        
        else :
            
            m = tag_re.match( segment )
            tag = m.group( 'tag' ).lower( )
            attrs = special_char_re.sub( special_char_sub , m.group( 'attrs' ) )
            
            if tag == 'html' : continue
                        
            if tag.startswith( '/' ) :
                begin_node = node
                while begin_node and begin_node.tag != tag[ 1 : ] : begin_node = begin_node.parent
                if begin_node : node = begin_node.parent
            else :
                if node.tag == tag and non_nestable_tag_re.match( tag ) : node = node.parent
                node.children.append( HtmlNode( node , tag , attrs ) )
                if not childless_tag_re.match( tag ) : node = node.children[ -1 ]           

    return html_tree



def get_interm_repr( html_tree ) :
    
    text = get_interm_repr_rec( html_tree )
    text = multi_nl_re.sub( '\n\n' , text )
    text = text.strip( '\n' ) + '\n' 

    return text



style_tag_str = r'a|b|big|em|h\d|i|small|strong|sub|sup|u'

caps_font_attr_re = re.compile( r'text-transform:\s*uppercase' , re.I )
bold_font_attr_re = re.compile( r'font-weight:\s*bold' , re.I )
inline_div_re = re.compile( r'inline' , re.I )

page_break_attr_re = re.compile( page_break_attr_str , re.I )
false_page_break_attr_re = re.compile( r':\s*avoid' , re.I )

non_discardable_block_tag_re = re.compile( r'^(' + non_discardable_block_tag_str + r')$' , re.I )
discardable_block_tag_re = re.compile( r'^(body|dd|dt|head|html|li|p|tbody|td|th|title|tr)$' , re.I )
style_tag_re = re.compile( r'^(' + style_tag_str + r')$' , re.I )



def get_interm_repr_rec( node , caps = False ) :
    
    keep_attrs = page_break_attr_re.search( node.attrs ) and not false_page_break_attr_re.search( node.attrs )    
    
    if node.tag == '!--' : return '<{}{}>'.format( node.tag , node.attrs ) if keep_attrs else ''
    if node.tag == 'br' : return '\n\n'
    if childless_tag_re.match( node.tag ) : return '\n\n<{}{}>\n\n'.format( node.tag , node.attrs )    
    
    if node.tag == 'font' :
        if caps_font_attr_re.search( node.attrs ) : caps = True
        if bold_font_attr_re.search( node.attrs ) : node.tag = 'b'
    
    text = ''.join( [ get_interm_repr_rec( child , caps ) if isinstance( child , HtmlNode ) else ( child.upper( ) if caps else child ) for child in node.children ] ) 
    
    if keep_attrs : return '\n\n<{}{}>\n\n{}\n\n'.format( node.tag , node.attrs , text ) # skip ending tag
    
    if node.tag == 'div' : return text if inline_div_re.search( node.attrs ) else '\n\n{}\n\n'.format( text )
    if discardable_block_tag_re.search( node.tag ) : return '\n\n{}\n\n'.format( text )
    if non_discardable_block_tag_re.search( node.tag ) : return '\n\n<{0}>\n\n{1}\n\n</{0}>\n\n'.format( node.tag , text )
    if style_tag_re.search( node.tag ) and text.strip( ) : return '<{0}>{1}</{0}>'.format( node.tag , text )
    
    return text



page_num_str = r'([A-Z]{1,3} *-? *)?\d{1,3}'

untagged_non_html_page_sep0_re = re.compile( r'(^|(?<=\n)) *(?P<footer_page_num>' + page_num_str + ') *\n+ *(?P<header_page_num>page *' + page_num_str + ') *((?=\n)|$)' , re.I )
untagged_non_html_page_sep0_sub_func = lambda m : '\n\n{}\n\n<PAGE>\n\n{}\n\n'.format( m.group( 'footer_page_num' ) , m.group( 'header_page_num' ) )

untagged_non_html_page_sep1_re = re.compile( r'(^|(?<=\n)) *<page *(?P<footer_page_num>' + page_num_str + ') *> *((?=\n)|$)' , re.I )
untagged_non_html_page_sep1_sub_func = lambda m : '\n\n{}\n\n<PAGE>\n\n'.format( m.group( 'footer_page_num' ) )

table_re = re.compile( r'<table( [^<>]*)?>(?P<body>.*?)</table>' , re.I | re.S )
num_in_table_str = r'[\$\(]?\d([\d,\.]*\d)?[%\)]?'
line_in_table_str = r'( *|[^\n]* )' + num_in_table_str + r'(  +' + num_in_table_str + r')+ *'
untagged_non_html_table_re = re.compile( r'(^|(?<=\n))' + line_in_table_str + r'(\n([^\n]*\n)?' + line_in_table_str + r')+((?=\n)|$)' , re.I )

non_html_tag_re = re.compile( r'<(/?table|page)>' , re.I )



def pre_parse_non_html( text ) :
    
    text = special_char_re.sub( special_char_sub , text )
    
    text = untagged_non_html_page_sep0_re.sub( untagged_non_html_page_sep0_sub_func , text )
    text = untagged_non_html_page_sep1_re.sub( untagged_non_html_page_sep1_sub_func , text )
    
    segments = split_by_re( text , table_re )
    for i in range( len( segments ) )[ : : 2 ] : segments[ i ] = untagged_non_html_table_re.sub( r'\n\n<table>\n\n\g<0>\n\n</table>\n\n' , segments[ i ] )
    text = ''.join( segments )
    
    text = non_html_tag_re.sub( r'\n\n\g<0>\n\n' , text )    
    text = multi_nl_re.sub( '\n\n' , text )
    text = text.strip( '\n' ) + '\n'    
    
    return text

