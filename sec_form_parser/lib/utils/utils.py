# lib/utils/utils.py
# Author: Rhaad M. Rabbani (2017)
# This file contains general utility functions intended for use by the user.



import re



# Utility function that splits text using regexp and retains regexp-matched parts

def split_by_re( text , regexp ) :
    
    ms = regexp.finditer( text )
    positions = [ 0 ] + [ pos for m in ms for pos in [ m.start( ) , m.end( ) ] ] + [ len( text ) ]
    segments = [ text[ positions[ i ] : positions[ i + 1 ] ] for i in range( len( positions ) - 1 ) ]
    
    return segments



# Utility function that groups items based on adjacency_check

def group_items( items , adjacency_check ) :
    
    groups = [ ]
    if items :
        groups.append( [ items[ 0 ] ] )
        for item in items[ 1 : ] :
            if adjacency_check( groups[ -1 ][ -1 ] , item ) : groups[ -1 ].append( item )
            else : groups.append( [ item ] )
            
    return groups



roman_re = re.compile( r'[ivx]+' )
roman_map = { 'i' : '1' , 'ii' : '2' , 'iii' : '3' , 'iv' : '4' , 'v' : '5' , 'vi' : '6' , 'ix' : '9' , 'x' : '10' , 'xi' : '11' }
roman_func = lambda m : roman_map[ m.group( ) ] if m.group( ) in roman_map else '?'



# Utility function that converts number string to int - handles roman numerals

def num_str_to_int( num_str ) :
    
    num_str = roman_re.sub( roman_func , num_str.lower( ) )
    
    if not roman_re.search( num_str ) : return int( num_str )
    else : return num_str
