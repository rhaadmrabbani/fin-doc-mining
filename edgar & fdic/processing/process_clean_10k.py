import re

from collections import defaultdict
from os import listdir, makedirs
from os.path import isdir


item_titles = defaultdict( set )


inp_dirpath = 'cleaned/10-K'
out_dirpath = 'sections/10-K'

#bad_filename_re = re.compile( r'2005-03-30-820067' )


def main( ) :
    opendir( '' )


filename_sortkey = lambda s: [ int( t ) for t in s[ : -4 ].split( '-' ) ] if s[ -4 : ] == '.txt' else s

def opendir( dirpath_suff ) :
    
    print inp_dirpath + dirpath_suff
    if not isdir( out_dirpath + dirpath_suff ) :
        makedirs( out_dirpath + dirpath_suff )
    
    filenames = listdir( inp_dirpath + dirpath_suff )
    filenames.sort( key = filename_sortkey )
    
    for filename in filenames[ : ] :
        if isdir( inp_dirpath + dirpath_suff + '/' + filename ) :
            opendir( dirpath_suff + '/' + filename )
        #elif '2005-03-15-920112.txt' == filename :#< '2015' :
        else :
            openfile( dirpath_suff + '/' + filename )


junk_re = re.compile( r'item 4\W*(\((removed and )?reserved\.?\)|\(reserved and removed\)|\[removed and reserved\])|(?<=\n)\W*(?=\n)', re.I | re.S )
table_re = re.compile( r'<table>.*?</table>', re.I | re.S )
tag_re = re.compile( r'<.*?>', re.I )
table_junk_re = re.compile( r'(^|(?<=\n))[^a-z\n]*\d+[^a-z\n]*((?=\n)|$)', re.I )
emph_tag_re = re.compile( r'</?[B]>', re.I )

def openfile( filepath_suff ) :
    
    print filepath_suff
    
    inp_file = open( inp_dirpath + filepath_suff, 'r' )
    text = inp_file.read( )
    inp_file.close( )

    #text = ''.join( re_split( table_re, lambda t : '' if table_junk_re.search( t ) else t, lambda t : t, text ) )
    text = junk_re.sub( '', text )
    #text = emph_tag_re.sub( '\n\n', text )
    process( text, filepath_suff[ : -4 ] )


doc_re = re.compile( r'^<DOCUMENT>\r?\n<TYPE>(?P<type>.*?)\r?\n(?P<text>.*?\r?\n)</DOCUMENT>(?P=type)', re.M | re.S )

def process( doc_text, dirpath_suff ) :

    process_10K( doc_text, dirpath_suff )


# TODO
# remove sections from table of contents
# fwd looking

multi_nl_re = re.compile( r'(\r?\n *){2,}' )
multi_spc_re = re.compile( r' {2,}' )
multi_dash_re = re.compile( r'(-|_){2,}' )
table_re = re.compile( r'<table>.*?</table>', re.I | re.S )

pageno_rstr = r'(((\d+|\*)(-|, *)|[A-Z]{1,3}-)?\d+\.?|\*{1,2}|[pP][aA][gG][eE] +\d+)($|\r?\n)'
nonitem_start_rstr = r'(?P<nonitem_start>([pP][aA][rR][tT]\s+[iI]|[sS][iI][gG][nN][aA][tT][uU][rR][eE][sS]))'
item_start_rstr = r'(?P<item_type>[iI][tT][eE][mM] +[\diIl]{1,2}\D*?)(\s|[A-Za-z]{2}|$)'
item2_start_rstr = r'(?P<item2_type>[iI][tT][eE][mM] +[\diIl]{1,2}\D*?)(\s|[A-Za-z]{2}|$)'
pseudoitem_start_rstr = r'(?P<pseudoitem_start>[iI][tT][eE][mM] +)'
title_rstr = r'(?P<title>[A-Z]\S*(\s+([A-Z]\S*|[a-z\d]\S{0,20}|&|\?\S+))*)$'

nonitem_item_hdrs_re = re.compile( nonitem_start_rstr + r'(\S*( *\S+)? *|.*?\r?\n *)' + item_start_rstr, re.S )
item_item_hdrs_re = re.compile( item2_start_rstr + r'.*?\r?\n *' + item_start_rstr, re.S )
pseudoitem_item_hdrs_re = re.compile( pseudoitem_start_rstr + r'.*?\r?\n *' + item_start_rstr, re.S )

table_start_re = re.compile( r'<table>', re.I )
table_end_re = re.compile( r'</table>', re.I )
nonitem_start_re = re.compile( nonitem_start_rstr )
item_start_re = re.compile( item_start_rstr )
pseudoitem_start_re = re.compile( pseudoitem_start_rstr )
toc_item_re = re.compile( item_start_rstr + r'.*?[\s\.]' + pageno_rstr, re.S )
pageno_re = re.compile( pageno_rstr )
title_re = re.compile( title_rstr )

punc_strip_re = re.compile( r'^[^A-Za-z\d\(\)]*(?P<text>.*?)[^A-Za-z\d\(\)]*$', re.S )
title_junk_re = re.compile( r'\r?\n\W*?(\r?\n|$)|\(.*?\)|/', re.S )
title_sep_re = re.compile( r'\.|\s(-|\?)?\s' )
title_sep2_re = re.compile( r'\r?\n[^\n]*? [a-z\d]\S{5}' )

title_guess_re = re.compile( r'^[^\n]+$', re.S )

item_num_re = re.compile( r'\d+' )
item_num_bad_re = re.compile( r'[iIlL]' )
def get_item_num( item ) :
    return int( item_num_re.search( item_num_bad_re.sub( '1' , item ) ).group( ) )


def process_10K( doc_text, dirpath_suff ) :

    doc_text = tag_re.sub( lambda m : m.group( ) if table_start_re.search( m.group( ) ) or table_end_re.search( m.group( ) ) else '' , doc_text )
    doc_text = junk_re.sub( '', doc_text )
    
    chunks = multi_nl_re.split( doc_text )
    chunks = [ c.strip( ) for c in chunks ]
    chunks = [ c for c in chunks if c ]
    chunks = [ multi_dash_re.sub( '--', multi_spc_re.sub( '  ', c ) ) for c in chunks ]
    
    chunk_idx = 0

    while chunk_idx < len( chunks ) :
        chunk = chunks[ chunk_idx ]

        if nonitem_item_hdrs_re.match( chunk ) :
            
            item_start = nonitem_item_hdrs_re.match( chunk ).start( 'item_type' )
            chunks[ chunk_idx : chunk_idx + 1 ] = [ chunk[ 0 : item_start ].strip( ), chunk[ item_start : ].strip( ) ]
            
        chunk_idx += 1

    chunk_idx = 0
    hdrs = [ ]
    table_start = -1
    table_item_count = 0
    last_item = -1

    while chunk_idx < len( chunks ) :
        chunk = chunks[ chunk_idx ]

        if table_start_re.match( chunk ) :
            hdrs.append( ( chunk_idx, 'table_start' ) )

        elif table_end_re.match( chunk ) :
            hdrs.append( ( chunk_idx, 'table_end' ) )

        elif nonitem_start_re.match( chunk ) :
            hdrs.append( ( chunk_idx, 'nonitem' ) )

        elif item_start_re.match( chunk ) :

            item_type_end = item_start_re.match( chunk ).end( 'item_type' )
            item_type = punc_strip_re.match( chunk[ 0 : item_type_end ] ).group( 'text' )
            item_rest = punc_strip_re.match( chunk[ item_type_end : ] ).group( 'text' )

            if last_item != -1 and chunks[ last_item ] == item_type :
                chunks[ chunk_idx : chunk_idx + 1 ] = [ ]
                continue

            if item_rest and title_guess_re.match( item_rest ) :
                item_rest = ' '.join( [ x.capitalize( ) for x in item_rest.split( ) ] )

            chunks[ chunk_idx : chunk_idx + 1 ] = [ item_type ] + ( [ item_rest ] if item_rest else [ ] )
            table_item_count += 1
            last_item = chunk_idx
            hdrs.append( ( chunk_idx, 'item' ) )

        elif pageno_re.match( chunk ) :
            hdrs.append( ( chunk_idx, 'pageno' ) )

        elif title_re.match( chunk ) :
            hdrs.append( ( chunk_idx, 'title' ) )              

        chunk = punc_strip_re.match( title_junk_re.sub( ' ', chunks[ chunk_idx ] ) ).group( 'text' )     

        if hdrs == [ ] or hdrs[ -1 ][ 0 ] < chunk_idx :

            if title_re.match( chunk ) :
                chunks[ chunk_idx ] = chunk
                hdrs.append( ( chunk_idx, 'title' ) )

            elif pageno_re.match( chunk ) :
                chunks[ chunk_idx ] = chunk
                hdrs.append( ( chunk_idx, 'pageno' ) )
            
            else :
                chunk = chunks[ chunk_idx ]
                '''if title_sep_re.search( chunk ) :
                    m = title_sep_re.search( chunk )
                    chunk1 = punc_strip_re.match( title_junk_re.sub( ' ', chunk[ : m.start( ) ] ) ).group( 'text' )
                    chunk2 = punc_strip_re.match( chunk[ m.start( ) + 1 : ] ).group( 'text' )
                    if title_re.match( chunk1 ) :
                        chunks[ chunk_idx : chunk_idx + 1 ] = [ chunk1 ] + ( [ chunk2 ] if chunk2 else [ ] )
                        hdrs.append( ( chunk_idx, 'title' ) )'''
                if hdrs and hdrs[ -1 ][ 1 ] == 'item' and title_sep2_re.search( chunk ) :
                    m = title_sep2_re.search( chunk )
                    chunk1 = punc_strip_re.match( title_junk_re.sub( ' ', chunk[ : m.start( ) ] ) ).group( 'text' )
                    chunk2 = punc_strip_re.match( chunk[ m.start( ) + 1 : ] ).group( 'text' )
                    if title_re.match( chunk1 ) :
                        chunks[ chunk_idx : chunk_idx + 1 ] = [ chunk1 ] + ( [ chunk2 ] if chunk2 else [ ] )
                        hdrs.append( ( chunk_idx, 'title' ) )

        chunk_idx += 1
    
    items = defaultdict( list )  
    
    hdr_idx = 0
    while hdr_idx < len( hdrs ) :
        chunk_idx1, chunk_type1 = hdrs[ hdr_idx ]
        
        if chunk_type1 != 'item' :
            hdr_idx += 1
            continue
        
        hdr_idx += 1
        while hdr_idx < len( hdrs ) :
            chunk_idx2, chunk_type2 =  hdrs[ hdr_idx ]
            if chunk_type2 in [ 'item' , 'nonitem' ] :
                break
            hdr_idx += 1
            
        if hdr_idx == len( hdrs ) :
            chunk_idx2 = len( chunks )

        if chunk_idx1 + 1 == chunk_idx2 :
            continue
        
        if table_start_re.match( chunks[ chunk_idx1 + 1 ] ) or re.compile( r'\(.*?\)|\(|\)' ).match( chunks[ chunk_idx1 + 1 ] ) :
            chunks[ chunk_idx1 + 1 : chunk_idx1 + 3 ] = [ chunks[ chunk_idx1 + 2 ] , chunks[ chunk_idx1 + 1 ] ]
            
        '''print '    ' + chunks[ chunk_idx1 ]
        print '    ' + chunks[ chunk_idx1 + 1 ]
        print'''

        item_num = re.compile( r'\W' ).sub( '' , chunks[ chunk_idx1 ].split( )[ 1 ] ).upper( )
        item_num2 = get_item_num( item_num )
        if not item_num2 in [ 1 , 7 ] :
            item_num = str( item_num2 )
        items[ item_num ] += chunks[ chunk_idx1 + 2 : chunk_idx2 ]       

    if not isdir( out_dirpath + dirpath_suff ) :
        makedirs( out_dirpath + dirpath_suff )
 
    for item_type in items :
        text = '\n\n'.join( items[ item_type ] )
        text = ''.join( re_split( table_re, lambda t : '' if len( table_junk_re.findall( t ) ) >= 2 else t , lambda t : t, text ) )
        out_file = open( out_dirpath + dirpath_suff + '/' +item_type + '.txt', 'w' )
        out_file.write( text )
        out_file.close( )


def re_split( regexp, m_lambda, non_m_lambda, text ):
    
    ms = [ m for m in regexp.finditer( text ) ]
    m_texts = [ m_lambda( m.group( ) ) for m in ms ]
    
    non_ms = zip( [ 0 ] + [ m.end( ) for m in ms ], [ m.start( ) for m in ms ] + [ len( text ) ] )
    non_m_texts = [ non_m_lambda( text[ s : e ] ) for s, e in non_ms ]
    
    return non_m_texts[ : 1 ] + [ t for ts in zip( m_texts, non_m_texts [ 1 : ] ) for t in ts ]


main( )

for x in sorted( item_titles ):
    print x + ' ' + str( sorted( item_titles[ x ] )[ : 5 ] )
#openfile( '/8-K/2012-11-26-860519.txt' )