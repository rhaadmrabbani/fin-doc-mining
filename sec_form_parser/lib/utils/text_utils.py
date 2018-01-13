# text_utils.py
# Author(s): Rhaad M. Rabbani (2017)

# This file contains text utility functions, strings and regular expressions intended for use by the user.



import re



##################################################################
## Strings and regular expressions intended for use by the user ##
##################################################################



tag_re = re.compile( r'(<(?P<tag>/?[!a-z][-\w]*)(?P<attrs>[^<>]*)>)' , re.I ) # matches HTML tag

table_re = re.compile( r'<table( [^<>]*)?>(?P<body>.*?)</table>' , re.I | re.S ) # matches table

page_num_str = r'([A-Z]{1,3} *-? *)?\d{1,3}'

non_discardable_block_tag_str = r'dir|dl|ol|pre|table|ul' # matches non-discardable blocks such as table, pre, etc

page_break_attr_str = r'page[^<>]*break|(?<=[^a-z])pg[^<>]*brk' # matches page-break related attribute(s) in tag

junky_nl_re = re.compile( r'\s*\n\s*' )



#########################################################
## Text utility functions intended for use by the user ##
#########################################################



# Utility function that splits text using regexp and retains regexp-matched parts

def split_by_re( text , regexp ) :
    
    ms = regexp.finditer( text )
    positions = [ 0 ] + [ pos for m in ms for pos in [ m.start( ) , m.end( ) ] ] + [ len( text ) ]
    segments = [ text[ positions[ i ] : positions[ i + 1 ] ] for i in range( len( positions ) - 1 ) ]
    
    return segments



# Utility function that splits text into lines, preserving blocks, e.g. table, pre, etc

def split_lines( text ) : return [ m.group( ) for m in line_re.finditer( text ) ]



# Utility function that joins lines and returns a single string

def join_lines( lines ) : return '\n'.join( lines )



# Utility function that splits text into paras, preserving blocks, e.g. table, pre, etc

def split_paras( text ) : return [ m.group( ).strip( '\n' ) for m in para_re.finditer( text ) ]



# Utility function that joins paras and returns a single string

def join_paras( paras ) : return '\n\n'.join( paras )



# Utility function that replaces every HTML special character by the appropriate ASCII character, if possible, or by ' '

def replace_special_chars( text ) : return special_char_re.sub( special_char_sub_func , text )



line_re = re.compile( r'(^|(?<=\n))( *<(?P<tag>' + non_discardable_block_tag_str + r')(\s[^<>]*)?>.*?</(?P=tag)> *|.*?)((?=\n)|$)' , re.I | re.S )

para_re = re.compile( r'(^|(?<=\n\n))(\s*<(?P<tag>' + non_discardable_block_tag_str + r')(\s[^<>]*)?>.*?</(?P=tag)> *|.*?)((?=\n\n)|$)' , re.I | re.S )

    

#######################################################
## Helper functions not intended for use by the user ##
#######################################################



def special_char_sub_func( m ) :
    
    code = m.group( 'code' )
    if code.startswith( '#' ) :
        if code[ 1 : ].startswith( 'x' ) and code[ 2 : ].isdigit( ) : code = '#' + str( int( code[ 2 : ] ) ) # hex to dec
        elif code[ 1 : ].isdigit( ) : code = '#' + str( int( code[ 1 : ] ) ) # remove leading zeros
    sub = special_char_map[ code ] if code in special_char_map else ' '
    
    return sub



special_char_re = re.compile( r'&(?P<code>.{1,6}?);' , re.S )

special_char_map = dict( [ ( k , v ) for ks , v in [ ( [ 'nbsp' , '#160' , '#9' ] , ' ' ) , ( [ 'amp' , '#38' ] , '&' ) , ( [ '#43' ] , ' + ' ) , ( [ 'lt' , '#60' ] , '<' ) , ( [ 'gt' , '#62' ] , '>' ) ,
                                                     ( [ '#91' ] , ' [ ' ) , ( [ '#93' ] , ' ] ' ) , ( [ '#95' ] , '_' ) , ( [ '&rsquo' , '#145' , '#146' , '#8216' , '#8217' ] , "'" ) ,
                                                     ( [ '&ldquo' , '&rdquo' ,  'quot' , '#147' , '#148' , '#8220' , '#8221' ] , '"' ) , ( [ '#150' , '#151' , '#8212' ] , ' - ' ) ] for k in ks ] )



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
