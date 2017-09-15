import os , os.path
import re


base_inp_dir = 'forms_int_rep'
base_out_dir = 'forms_int_rep_wordlist_filtered'
wordlist_filepath = 'WordList_Derivatives.txt'


paren_re = re.compile( r'\s*\((.*?)\)' )


inp = open( wordlist_filepath )
lines = inp.readlines( )
inp.close( )

lines = [ line.strip( ).lower( ) for line in lines ]
#lines = lines[ : lines.index( 'rule names:' ) - 1 ]
lines = lines[ : lines.index( 'rule names:' ) - 1 ] + lines[ lines.index( 'rule names:' ) + 1 : ]

lines1 = [ paren_re.sub( r'|\1' , line ).replace( ' ' , r'\s' ) for line in lines ]
enum_lines = [ r'(?P<g{}>{})'.format( index , line ) for index , line in enumerate( lines1 ) ]
wordlist_re = re.compile( '|'.join( enum_lines ) )

repl_lines = [ paren_re.sub( r'' , line ).replace( ' ' , r'_' ) for line in lines ]


for sic in os.listdir( base_inp_dir ) :
    
    inp_files = os.listdir( base_inp_dir + '/' + sic )
    print sic , len( inp_files )
    
    if not os.path.isdir( base_out_dir + '/' + sic ) :
        os.makedirs( base_out_dir + '/' + sic )
    
    for inp_file in inp_files :
        
        inp = open( base_inp_dir + '/' + sic + '/' + inp_file )
        text = inp.read( )
        inp.close( )
        
        words = [ ]
        for m in wordlist_re.finditer( text ) :
            for i in range( len( enum_lines ) ) :
                if m.group( 'g{}'.format( i ) ) :
                    words.append( repl_lines[ i ] )
        text = ' '.join( words )
        
        out = open( base_out_dir + '/' + sic + '/' + inp_file , 'w' )
        out.write( text )
        out.close( )
