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


class Node :
    
    def __init__( self , parent , tag , attr ) :
        self.parent = parent
        self.level = parent.level + 1 if parent else 0
        self.tag = tag
        self.attr = attr
        self.children = [ ]
        

sp_char_re = re.compile( r'&(?P<code>.{1,6}?);' , re.S )

sp_char_map = dict( [ ( k , v ) for ks , v in [ ( [ 'nbsp' , '#160' , '#9' ] , ' ' ) ,
                                                ( [ 'amp' , '#38' ] , '&' ) ,
                                                ( [ '#43' ] , ' + ' ) ,
                                                ( [ 'lt' , '#60' ] , '<' ) ,
                                                ( [ 'gt' , '#62' ] , '>' ) ,
                                                ( [ '#91' ] , ' [ ' ) ,
                                                ( [ '#93' ] , ' ] ' ) ,
                                                ( [ '#95' ] , '_' ) ,
                                                ( [ '&rsquo' , '#145' , '#146' , '#8216' , '#8217' ] , "'" ) ,
                                                ( [ '&ldquo' , '&rdquo' ,  'quot' , '#147' , '#148' , '#8220' , '#8221' ] , '"' ) ,
                                                ( [ '#150' , '#151' , '#8212' ] , ' - ' ) ] for k in ks ] )


def sp_char_sub( m ) :
    
    code = m.group( 'code' )

    if code.startswith( '#' ) :
        if code[ 1 : ].startswith( 'x' ) and code[ 2 : ].isdigit( ) : code = '#' + str( int( code[ 2 : ] ) ) # hex to dec
        elif code[ 1 : ].isdigit( ) : code = '#' + str( int( code[ 1 : ] ) ) # remove leading zeros		 

    sub = sp_char_map[ code ] if code in sp_char_map else ' '
    return sub 


page_attr_str = r'page[^<>]*break|(?<=[^a-z])pg[^<>]*brk'


tab_re = re.compile( r'\t' )
    
multi_nl_re = re.compile( r'\s*\r?\n\s*\r?\n\s*' )

tag_re = re.compile( r'(<(/?[!a-z][^\s<>/]*)([^>]*)>)' , re.I )

html_re = re.compile( r'html' , re.I )

nonhtml_inner_tag_re = re.compile( r'(?<=\n)\s*(<[^<>]*>|<page> +\d{1,3})\s*(?=\n)' ,re.I )

nl_re = re.compile( r'\s*\r?\n\s*' )

page_attr_re = re.compile( page_attr_str , re.I )

not_page_attr_re = re.compile( r':\s*avoid' , re.I )


# return parsed html tree given html text


def get_html_tree( text ) :
    
    tokens = tag_re.split( text )
    
    # find <html> tag
    is_html = False
    for i in range( len( tokens ) )[ : -1 : 4 ] :
        if tokens[ i + 2 ].lower( ) in [ 'html' , 'title' ] \
        or tokens[ i + 2 ].lower( ) == '!doctype' and html_re.search( tokens[ i + 3 ].lower( ) ) :
            is_html = True
            break
    
    # if <html> not found, wrap text within a <nonhtml> node and return
    if not is_html :
        nonhtml = Node( None , 'nonhtml' , '' )
        text = sp_char_re.sub( sp_char_sub , text )
        text = tab_re.sub( ' ' , text )
        text = nonhtml_inner_tag_re.sub( r'\n\g<0>\n' , text )
        text = multi_nl_re.sub( '\n\n' , text ).strip( ) + '\n'
        nonhtml.children.append( text )
        return nonhtml
    
    # Build html tree
    
    # create root node 'html', use 'node' as current node
    html = Node( None , 'html' , '' ) 
    node = html
    
    # iterate through tokens and build html tree
    # tokens[ i ] is string before tag
    # tokens[ i + 1 ] is entire tag including attr
    # tokens[ i + 2 ] is tag's keyword
    # tokens[ i + 3 ] is tag's attr
    for i in range( len( tokens ) )[ i + 4 : : 4 ] :
        
        token = tokens[ i ]
        token = sp_char_re.sub( sp_char_sub , token )
        
        # after last token read, return html tree
        if i == len( tokens ) - 1 or not node :
            return html
        
        # if current node is <pre>
        if node.tag == 'pre' :
            if token : node.children.append( token )
            tag = tokens[ i + 2 ].lower( )
            if tag == '/pre' :
                node = node.parent
            else :
                token = tokens[ i + 1 ]
                token = sp_char_re.sub( sp_char_sub , token )                
                if token : node.children.append( token )
            continue
        
        # handle text before tag
        token = nl_re.sub( ' ' , token )
        if token : node.children.append( token )
        
        # handle tag
        tag = tokens[ i + 2 ].lower( )
        attr = nl_re.sub( ' ' , sp_char_re.sub( sp_char_sub , tokens[ i + 3 ] ) )
        
        if tag.startswith( '/' ) :
            begin_node = node
            while begin_node and begin_node.tag != tag[ 1 : ] : begin_node = begin_node.parent
            if begin_node : node = begin_node.parent
        elif tag == 'br' :
            node.children.append( '\n\n' )
        elif tag in [ 'page' , 'hr' ] :
            node.children.append( '\n\n<' + tag + attr + '>\n\n' )
        elif tag == '!--' :
            if page_attr_re.search( html.attr ) : node.children.append( '<' + tag + attr + '>' )        
        else :            
            if tag in [ 'dir' , 'ol' , 'p' , 'table' , 'ul' ] and node.tag == tag : node = node.parent # don't nest paragraph nodes             
            node.children.append( Node( node , tag , attr ) )
            node = node.children[ -1 ]

			
# Get simplified text version of html_tree that retains minimal tags

def get_simplified_text( html ) :
    
    text = get_simplified_text_helper( html )
    text = tab_re.sub( ' ' , text )
    text = multi_nl_re.sub( '\n\n' , text ).strip( ) + '\n'
    
    return text


# Helper functions


font_attr_caps_re = re.compile( r'text-transform:\s*uppercase' , re.I )

font_attr_bold_re = re.compile( r'font-weight:\s*bold' , re.I )

div_inline_re = re.compile( r'inline' , re.I )

discard_non_inline_tag_re = re.compile( r'^(body|dd|dt|head|li|p|tbody|td|title|th|tr)$' , re.I )

keep_non_inline_tag_re = re.compile( r'^(dir|dl|html|nonhtml|o|pre|table|ul)$' , re.I )

keep_inline_tag_re = re.compile( r'^(a|b|big|em|h\d|i|small|strong|sub|sup|u)$' , re.I )


def get_simplified_text_helper( html , caps = False ) :

    if html.tag == 'font' and font_attr_caps_re.search( html.attr ) : caps = True
    if html.tag == 'font' and font_attr_bold_re.search( html.attr ) : html.tag = 'b'
    
    text = ''    
    
    for child in html.children :
        if isinstance( child , Node ) :
            text += get_simplified_text_helper( child , caps )
        else :
            text += ( child if not caps else child.upper( ) )    
    
    if html.tag == 'div' :
        if page_attr_re.search( html.attr ) and not not_page_attr_re.search( html.attr ) :
            text = '<' + html.tag + str( html.level ) + html.attr + '>' + text + '</' + html.tag + str( html.level ) + '>'
        if not div_inline_re.search( html.attr ) : text = '\n\n' + text + '\n\n'
        return text
    elif discard_non_inline_tag_re.search( html.tag ) :
        if page_attr_re.search( html.attr ) and not not_page_attr_re.search( html.attr ) :
            text = '<' + html.tag + html.attr + '>' + text + '</' + html.tag + '>'
        return '\n\n' + text + '\n\n'
    elif keep_non_inline_tag_re.search( html.tag ) :
        return '\n\n<' + html.tag \
               + ( html.attr if page_attr_re.search( html.attr ) and not not_page_attr_re.search( html.attr ) else '' ) \
               + '>\n\n' + text + '\n\n</' + html.tag + '>\n\n'
    elif not text.strip( ) :
        if page_attr_re.search( html.attr ) and not not_page_attr_re.search( html.attr ) :
            text = '<' + html.tag + html.attr + '>' + text + '</' + html.tag + '>'
        return text
    elif keep_inline_tag_re.search( html.tag ) :
        return '<' + html.tag \
               + ( html.attr if page_attr_re.search( html.attr ) and not not_page_attr_re.search( html.attr ) else '' ) \
               + '>' + text + '</' + html.tag + '>'
    else :
        if page_attr_re.search( html.attr ) and not not_page_attr_re.search( html.attr ) :
            text = '<' + html.tag + html.attr + '>' + text + '</' + html.tag + '>'
        return text



