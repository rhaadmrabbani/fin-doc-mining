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


import os , os.path
import re


tag_re = re.compile( r'(<(/?[^\s>/]*)([^>]*)>)' )

sp_char_re = re.compile( r'&(?P<code>.{1,6}?);' , re.S )

sp_char_map = dict( [ ( k , v ) for ks , v in [ ( [ 'nbsp' , '#160' , '#9' , '#09' , '#009' ] , ' ' ) ,
                                                ( [ 'amp' , '#38' , '#038' ] , '&' ) ,
                                                ( [ '#43' , '#043' ] , ' + ' ) ,
                                                ( [ 'lt' , '#60' , '#060' ] , '<' ) ,
                                                ( [ 'gt' , '#62' , '#062' ] , '>' ) ,
                                                ( [ '#91' , '#091' ] , ' [ ' ) ,
                                                ( [ '#93' , '#093' ] , ' ] ' ) ,
                                                ( [ '#95' , '#095' ] , '_' ) ,
                                                ( [ '&rsquo' , '#145' , '#146' , '#8216' , '#8217' ] , "'" ) ,
                                                ( [ '&ldquo' , '&rdquo' ,  'quot' , '#147' , '#148' , '#8220' , '#8221' ] , '"' ) ,
                                                ( [ '#150' , '#151' , '#8212' ] , ' - ' ) ] for k in ks ] )

nl_re = re.compile( r'\s*\r?\n\s*' )

page_re = re.compile( r'page' , re.I )

font_attr_caps_re = re.compile( r'text-transform:\s*uppercase' , re.I )

div_top_gap_re = re.compile( r'(margin|padding)-top' , re.I )

div_bottom_gap_re = re.compile( r'(margin|padding)-bottom' , re.I )

multi_nl_re = re.compile( r'\s*\r?\n\s*\r?\n\s*' )


class Node :
    
    def __init__( self , parent , tag , attr ) :
        self.parent = parent
        self.tag = tag
        self.attr = attr
        self.children = [ ]


def sp_char_sub( m ) :
    
    code = m.group( 'code' )
    return sp_char_map[ code ] if code in sp_char_map else '?'


def prune_html( html ) :
    
    children = [ ]
    for child in html.children :
        if not isinstance( child , Node ) :
            children.append( child )
        else :
            prune_html( child )
            if child.children : children.append( child )
    html.children = children


def get_html( text ) :
    
    html = Node( None , 'html' , '' )        
    
    tokens = tag_re.split( text )
    
    is_html = False
    for i in range( len( tokens ) )[ : -1 : 4 ] :
        if tokens[ i + 2 ].lower( ) in [ 'html' , 'title' ] :
            is_html = True
            break
        
    if not is_html :
        text = sp_char_re.sub( sp_char_sub , text )
        html.children.append( text )
        return html
    
    node = html
    
    for i in range( len( tokens ) )[ i + 4 : : 4 ] :
        
        token = tokens[ i ]
        token = sp_char_re.sub( sp_char_sub , token )
        
        if i == len( tokens ) - 1 :
            prune_html( html )
            return html
        
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
        
        token = nl_re.sub( ' ' , token )
        if token : node.children.append( token )
        
        tag = tokens[ i + 2 ].lower( )
        attr = tokens[ i + 3 ]
        
        if tag.startswith( '/' ) :
            begin_node = node
            while begin_node and begin_node.tag != tag[ 1 : ] : begin_node = begin_node.parent
            if begin_node : node = begin_node.parent            
        elif tag in [ 'br' , 'page' , 'hr' , '!--' ] :
            node.children.append( '<{}>'.format( tag ) )         
        else :
            if tag == 'p' and node.tag == 'p' : node = node.parent              
            node.children.append( Node( node , tag , attr ) )
            node = node.children[ -1 ]


def get_simplified_text_list( html , caps = False ) :

    text_list = [ ]

    if html.tag == 'div' :
        if div_top_gap_re.search( html.attr ) : text_list += [ '\n\n' ]
    elif html.tag == 'font' :
        if font_attr_caps_re.search( html.attr ) : caps = True
    elif html.tag in [ 'head' , 'body' , 'p' , 'tr' , 'td' , 'li' ] :
        text_list += [ '\n\n' ]
    elif html.tag in [ 'table' , 'ul' ] :
        text_list += [ '\n\n<' , html.tag , '>\n\n' ]
    else :
        text_list += [ '<' , html.tag , '>' ]
    
    for child in html.children :
        if isinstance( child , Node ) :
            text_list += get_simplified_text_list( child , caps )
        elif child.startswith( '<br' ) :
            text_list += [ '\n\n' ]
        else :
            text_list += [ child if not caps else child.upper( ) ]
    
    if html.tag == 'div' :
        if div_bottom_gap_re.search( html.attr ) : text_list += [ '\n\n' ]      
    elif html.tag == 'font' :
        pass   
    elif html.tag in [ 'head' , 'body' , 'p' , 'tr' , 'td' , 'li' ] :
        text_list += [ '\n\n' ]
    elif html.tag in [ 'table' , 'ul' ] :
        text_list += [ '\n\n</' , html.tag , '>\n\n' ]
    else :
        text_list += [ '</' , html.tag , '>' ]
    
    return text_list


def get_simplified_text( html ) :
    
    text = ''.join( get_simplified_text_list( html ) )
    text = multi_nl_re.sub( '\n\n' , text )
    
    return text
  