# lib/utils/text_utils.py
# Author: Rhaad M. Rabbani (2017)
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



line_re = re.compile( r'(^|(?<=\n))( *<(?P<tag>' + non_discardable_block_tag_str + r')(\s[^<>]*)?>.*?</(?P=tag)> *|.*?)((?=\n)|$)' , re.I | re.S )

para_re = re.compile( r'(^|(?<=\n\n))( *<(?P<tag>' + non_discardable_block_tag_str + r')(\s[^<>]*)?>.*?</(?P=tag)> *|.*?)((?=\n\n)|$)' , re.I | re.S )



# Utility function that splits text into lines, preserving blocks, e.g. table, pre, etc

def split_lines( text ) : return [ m.group( ) for m in line_re.finditer( text ) ]



# Utility function that joins lines and returns a single string

def join_lines( lines ) : return '\n'.join( lines )



# Utility function that splits text into paras, preserving blocks, e.g. table, pre, etc

def split_paras( text ) : return [ m.group( ) for m in para_re.finditer( text ) ]



# Utility function that joins paras and returns a single string

def join_paras( paras ) : return '\n\n'.join( paras )



# Utility function that replaces every HTML special character by the appropriate ASCII character, if possible, or by ' '

def replace_special_chars( text ) : return special_char_re.sub( special_char_sub_func , text )



roman_re = re.compile( r'[ivx]+' )

roman_map = { 'i' : '1' , 'ii' : '2' , 'iii' : '3' , 'iv' : '4' , 'v' : '5' , 'vi' : '6' , 'ix' : '9' , 'x' : '10' , 'xi' : '11' }

roman_func = lambda m : roman_map[ m.group( ) ] if m.group( ) in roman_map else '?'



# Utility function that converts number string to int - handles roman numerals

def convert_str_to_int( num_str ) :
    
    num_str = roman_re.sub( roman_func , num_str.lower( ) )
    
    if not roman_re.search( num_str ) : return int( num_str )
    else : return num_str
    
    

#######################################################
## Helper functions not intended for use by the user ##
#######################################################



special_char_re = re.compile( r'&(?P<code>.{1,6}?);' , re.S )

special_char_map = dict( [ ( k , v ) for ks , v in [ ( [ 'nbsp' , '#160' , '#9' ] , ' ' ) , ( [ 'amp' , '#38' ] , '&' ) , ( [ '#43' ] , ' + ' ) , ( [ 'lt' , '#60' ] , '<' ) , ( [ 'gt' , '#62' ] , '>' ) ,
                                                     ( [ '#91' ] , ' [ ' ) , ( [ '#93' ] , ' ] ' ) , ( [ '#95' ] , '_' ) , ( [ '&rsquo' , '#145' , '#146' , '#8216' , '#8217' ] , "'" ) ,
                                                     ( [ '&ldquo' , '&rdquo' ,  'quot' , '#147' , '#148' , '#8220' , '#8221' ] , '"' ) , ( [ '#150' , '#151' , '#8212' ] , ' - ' ) ] for k in ks ] )



def special_char_sub_func( m ) :
    
    code = m.group( 'code' )
    if code.startswith( '#' ) :
        if code[ 1 : ].startswith( 'x' ) and code[ 2 : ].isdigit( ) : code = '#' + str( int( code[ 2 : ] ) ) # hex to dec
        elif code[ 1 : ].isdigit( ) : code = '#' + str( int( code[ 1 : ] ) ) # remove leading zeros
    sub = special_char_map[ code ] if code in special_char_map else ' '
    
    return sub

    