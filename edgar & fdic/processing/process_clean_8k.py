import re

from collections import defaultdict
from os import listdir, makedirs
from os.path import isdir
from difflib import SequenceMatcher





inp_dirpath = 'cleaned/8-K'
out_dirpath = 'sections/8-K'


def main( ) :
    opendir( '' )


filename_sortkey = lambda s: [ int( t ) for t in s[ : -4 ].split( '-' ) ] if s[ -4 : ] == '.txt' else s

def opendir( dirpath_suff ) :
    
    print inp_dirpath + dirpath_suff
    if not isdir( out_dirpath + dirpath_suff ) :
        makedirs( out_dirpath + dirpath_suff )
    
    filenames = listdir( inp_dirpath + dirpath_suff )
    filenames.sort( key = filename_sortkey )
    
    for filename in filenames :
        if isdir( inp_dirpath + dirpath_suff + '/' + filename ) :
            opendir( dirpath_suff + '/' + filename )
        elif '2016-07-29' <= filename : # < '2015' :
        #else :
            openfile( dirpath_suff + '/' + filename )


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
    #text = emph_tag_re.sub( '\n\n', text )
    process( text, filepath_suff[ : -4 ] )


doc_re = re.compile( r'^<DOCUMENT>\r?\n<TYPE>(?P<type>.*?)\r?\n(?P<text>.*?\r?\n)</DOCUMENT>(?P=type)', re.M | re.S )

def process( doc_text, dirpath_suff ) :

    process_8K( doc_text, dirpath_suff )


# TODO
# remove sections from table of contents
# fwd looking

multi_nl_re = re.compile( r'(\r?\n *){2,}' )
multi_spc_re = re.compile( r' {2,}' )
multi_dash_re = re.compile( r'(-|_){2,}' )

dbl_item_hdr_re1 = re.compile( r'(?P<hdr1>item\W? +\d+\.\d+\D*?)( +and|;|,) +(item\W? +)?(?P<type2>\d+\.\d+)', re.I )
dbl_item_hdr_re2 = re.compile( r'(?P<hdr1>item\W? +\d+\.\d+.*?)\r?\n *(?P<hdr2>item\W? +\d+\.\d+)', re.I | re.S )
item_nonitem_hdrs_re = re.compile( r'(?P<hdr1>item\W? +\d+\.\d+.*?)\r?\n *(?P<hdr2>(signature|section|exhibit\s))', re.I | re.S )
nonitem_item_hdrs_re = re.compile( r'(?P<hdr1>(signature|section|exhibit\s).*?)\r?\n *(?P<hdr2>item\W? +\d+\.\d+)', re.I | re.S )

table_start_re = re.compile( r'<table>' )
table_end_re = re.compile( r'</table>' )
nonitem_hdr_re = re.compile( r'signature|section|exhibit\s', re.I )

item_hdr_start_re = re.compile( r'item\W? +(?P<type>\d+\.\d+)', re.I )
toc_item_hdr_re = re.compile( r'.*?\s\d$', re.S )

item_type_rstr = r'(?P<type>[iI][tT][eE][mM]\W? +\d+\.\d+)'
item_title_strict_rstr = r'(\(.*?\)|\W|[a-z]\.)*(?P<title>[A-Z][^\d\s]*(\s+([A-Z][^\d\s]*|[a-z][^\d\s]{0,4}))*?)\W*?'
item_title_rstr = r'(\(.*?\)|\W|[a-z]\.|and)*(\d*)(?P<title>[A-Z]\D*?)\W*?'
desc_start_rstr = r'(?P<desc>(--|\.|\(.*?\)|:|\s(\?|-|In|On|See|A copy)\s))'

item_hdr_strict_re = re.compile( item_type_rstr + r'(' + item_title_strict_rstr + r'|\W*?)$', re.S )
item_hdr_desc_re = re.compile( item_type_rstr + r'(' + item_title_rstr + r'|\W*?)' + desc_start_rstr, re.S )
item_hdr_re = re.compile( item_type_rstr + r'(' + item_title_rstr + r'|\W*?)$', re.S )

item_title_strict_re = re.compile( item_title_strict_rstr + r'$', re.S )
item_title_strict_desc_re = re.compile( item_title_strict_rstr + desc_start_rstr, re.S )
item_title_re = re.compile( item_title_rstr + r'$', re.S )

item_junk_re = re.compile( r'\r?\n|-{2}|_| +' )


sec_hdr_re = re.compile( r'(^|\n)<SEC-HEADER>\n(?P<infos>.*?)</SEC-HEADER>' , re.S )
item_info_re = re.compile( r'(^|\n)ITEM INFORMATION: (?P<name>[^\n]*)' )    


def process_8K( doc_text, dirpath_suff ) :

    item_infos_m = sec_hdr_re.match( doc_text )
    item_infos = item_infos_m.group( 'infos' )
    item_names = [ m.group( 'name' ) for m in item_info_re.finditer( item_infos ) ]
    
    doc_text = doc_text[ item_infos_m.end( ) : ]

    doc_text = tag_re.sub( lambda m : m.group( ) if table_start_re.search( m.group( ) ) or table_end_re.search( m.group( ) ) else '' , doc_text )
    chunks = multi_nl_re.split( doc_text )
    chunks = [ c.strip( ) for c in chunks ]
    chunks = [ c for c in chunks if c ]
    chunks = [ multi_dash_re.sub( '--', multi_spc_re.sub( '  ', c ) ) for c in chunks ]

    for chunk_idx in range( len( chunks ) ) :
        chunk = chunks[ chunk_idx ]

        m = dbl_item_hdr_re1.match( chunk )
        if m :
            chunks[ chunk_idx : chunk_idx + 1 ] = [ m.group( 'hdr1' ).strip( ), 'Item ' + chunk[ m.start( 'type2' ) : ].strip( ) ]
            continue

        m = dbl_item_hdr_re2.match( chunk ) or item_nonitem_hdrs_re.match( chunk ) or nonitem_item_hdrs_re.match( chunk )
        if m :
            chunks[ chunk_idx : chunk_idx + 1 ] = [ m.group( 'hdr1' ).strip( ), chunk[ m.start( 'hdr2' ) : ] ]
            continue

    hdrs = [ ]

    for chunk_idx in range( len( chunks ) ) :
        chunk = chunks[ chunk_idx ]

        if table_start_re.match( chunk ) :
            hdrs.append( ( chunk_idx, 'table_start' ) )
            continue

        if table_end_re.match( chunk ) :
            hdrs.append( ( chunk_idx, 'table_end' ) )
            continue

        if nonitem_hdr_re.match( chunk ):
            hdrs.append( ( chunk_idx, 'nonitem' ) )
            continue

        if not item_hdr_start_re.match( chunk ) or toc_item_hdr_re.match( chunk ):
            continue
        
        m = item_hdr_start_re.match( chunk )
        if m and int( m.group( 'type' ).split( '.' )[ 0 ] ) >= 20 :
            continue

        m = item_hdr_strict_re.match( chunk )
        if m :
            item_type = m.group( 'type' ).strip( )
            chunks[ chunk_idx ] = item_type
            item_title = m.group( 'title' )
            if item_title:
                chunks[ chunk_idx + 1 : chunk_idx + 1 ] = [ item_title ]
            hdrs.append( ( chunk_idx, 'item' ) )
            continue

        m = item_hdr_desc_re.match( chunk )
        if m :
            item_type = m.group( 'type' ).strip( )
            item_title = m.group( 'title' ) or ''
            item_desc = chunk[ m.start( 'desc' ) : ].strip( )
            chunks[ chunk_idx : chunk_idx + 1 ] = [ item_type, item_title, item_desc ]
            hdrs.append( ( chunk_idx, 'item' ) )
            continue

        m = item_hdr_re.match( chunk )
        if m :
            item_type = m.group( 'type' ).strip( )
            item_title = m.group( 'title' )

        if m and not item_title :
            chunks[ chunk_idx ] = item_type
            hdrs.append( ( chunk_idx, 'item' ) )
            continue

        if m and len( item_title ) < 200 :
            chunks[ chunk_idx : chunk_idx + 1 ] = [ item_type, item_title ]            
            hdrs.append( ( chunk_idx, 'table_item' if hdrs and hdrs[ -1 ][ 1 ] in \
                                      [ 'table_start', 'table_item', 'table_nonitem' ] else 'item' ) )
            continue

        m = re.compile( item_type_rstr + r'\W*(?P<title>[A-Z][A-Z][A-Z ]*)(?P<desc>.*?)$', re.S ).match( chunk )
        m2 = re.compile( re.compile( item_type_rstr + r'(' + item_title_strict_rstr + r')(?P<desc>(The (following )?information|At the |This Current Report on|The response to|Beginning|Issuance).*)$', re.S ) ).match( chunk )
        if m or m2 :
            item_type = ( m or m2 ).group( 'type' ).strip( )
            item_title = ( m or m2 ).group( 'title' )
            item_desc = ( m or m2 ).group( 'desc' )
            chunks[ chunk_idx : chunk_idx + 1 ] = [ item_type, item_title , item_desc ]            
            hdrs.append( ( chunk_idx, 'table_item' if hdrs and hdrs[ -1 ][ 1 ] in \
                                      [ 'table_start', 'table_item', 'table_nonitem' ] else 'item' ) ) 
            continue            

        m = re.compile( item_type_rstr + r'\s*(,|is |of |above )' ).match( chunk )
        if m :
            continue

        print [ chunk ]
        exit( 1 )

    item_sections = [ ]
    hdr_idx = 0

    while hdr_idx < len( hdrs ):
        chunk_idx, hdr_type = hdrs[ hdr_idx ]

        if hdr_type == 'item' :

            hdr_idx2 = hdr_idx + 1

            while hdr_idx2 < len( hdrs ) :
                chunk_idx2, hdr_type2 = hdrs[ hdr_idx2 ]
                if hdr_type2 in [ 'item', 'nonitem' ] :
                    break
                hdr_idx2 += 1

            if hdr_idx2 == len( hdrs ) :
                item_sections.append( chunks[ chunk_idx : ] )
                break
            else :
                item_sections.append( chunks[ chunk_idx : chunk_idx2 ] )
                hdr_idx = hdr_idx2

        else :
            hdr_idx += 1

    print str( len( item_sections ) ) + ' item section(s)'

    items = defaultdict( list )

    item_titles = defaultdict( set )

    for section in item_sections :

        while ( True ) :

            if len( section ) == 1 :
                item_title = ''
                section.append( '' )
                break

            section[ 1 ] = section[ 1 ].strip( )
            if section[ 1 ] == '' :
                break

            m = item_title_strict_re.match( section[ 1 ] )
            if m :
                section[ 1 ] = m.group( 'title' )
                break

            m = item_title_strict_desc_re.match( section[ 1 ] )
            if m :
                item_title = m.group( 'title' )
                item_desc = section[ 1 ][ m.start( 'desc' ) : ].strip( )
                section[ 1 : 2 ] = [ item_title, item_desc ]
                break

            m = item_title_re.match( section[ 1 ] )
            if m and len( section[ 1 ] ) < 200 :
                section[ 1 ] = m.group( 'title' )

            section[ 1 : 1 ] = [ '' ]
            break

        section[ 0 ] = item_hdr_start_re.match( section[ 0 ] ).group( 'type' )
        if section[ 1 ] : #and not section[ 0 ].startswith( '9' ):
            section[ 1 ] = item_junk_re.sub( ' ', item_title_re.match( section[ 1 ] ).group( 'title' ) ).lower( )
            item_titles[ section[ 0 ] ].add( section[ 1 ] )
            items[ section[ 0 ] ].append( '\n\n'.join( section[ 2 : ] ) )

        print ( section[ 0 ], section[ 1 ] )
    print item_names
    print

    if not isdir( out_dirpath + dirpath_suff ) :
        makedirs( out_dirpath + dirpath_suff )
 
    for item_type in items :
        text = '\n\n'.join( items[ item_type ] )
        text = ''.join( re_split( table_re, lambda t : '' if len( table_junk_re.findall( t ) ) >= 2 else t, lambda t : t, text ) )
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

#for x in sorted( item_titles ):
#    print x + ' ' + str( sorted( item_titles[ x ] )[ : 5 ] )
#openfile( '/8-K/2012-11-26-860519.txt' )