import os
import re
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

import difflib
differ = difflib.Differ( )

import sys
sys.path.append('../data')
import csv_utils



mast_dict = csv_utils.parse_csv( 'LoughranMcDonald_MasterDictionary_2016.csv' , headers = [ 'Word' , 'Negative' , 'Positive' , 'Uncertainty' , 'Litigious' ] )[ 1 : ]
mast_dict = dict( [ ( stemmer.stem( entry[ 0 ].lower( ) ) , [ 0 if val == '0' else 1 for val in entry[ 1 : ] ] ) for entry in mast_dict if entry[ 1 : ] != [ '0' ] * 4 ] )



tag_re = re.compile( r'<.*?>' )

page_sep_re = re.compile( r'(^|\n\s*\n)?(page [^\n]*|-? *\d+ *-?)(\n\s*\ntable of contents?)?(\n\s*\n|$)' , re.I )
bad_page_end_re = re.compile( r'[\w,]$' )
bad_page_start_re = re.compile( r'^[a-z]' )

para_sep_re = re.compile( r'\n\s*\n|\.  ' , re.I )
para_sep_re2 = re.compile( r'\. ?(?=(Accordingly|Actions|Any|As|Because|Changes|Consequently|Expansion|Failure|Further|Future|However|If|In|Investors|Our|Management|Many|Market|Material|Moreover|Recently|See|The|There|This|Unpredictable|We|With)[, ])' )


def get_paras( inp_path ) :
    
    inp = open( inp_path )
    text = inp.read( )
    inp.close( )    
    
    text = tag_re.sub( '' , text )
    pages = page_sep_re.split( text )[ : : 5 ]

    i = 0
    while i < len( pages ) - 1 :
        if bad_page_end_re.search( pages[ i ] ) and bad_page_start_re.search( pages[ i + 1 ] ) :
            pages[ i : i + 2 ] = [ pages[ i ] + ' ' + pages[ i + 1 ] ]
            continue
        i += 1  
    
    text = '\n\n'.join( pages )
    paras = [ para.strip( ) for para in para_sep_re.split( text ) if para.strip( ) ]
    paras = [ p for para in paras for p in para_sep_re2.split( para )[ : : 2 ] ]
    paras = [ para + '.' if bad_page_end_re.search( para ) else para for para in paras ]
    
    
    return paras



cik_to_fy = dict( [ ( cik , fy ) for cik, fy in csv_utils.parse_csv( '../data/old/cik&fys.txt' ) ] )

base_inp_dir = '../py13/sections/10-K'
inp_dir_re = re.compile( r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<cik>\d+)' )

cik_to_inp_dirs_f = defaultdict( list )
cik_to_inp_dirs_nf = defaultdict( list )


for inp_dir in os.listdir( base_inp_dir ) :
    
    inp_dir_m = inp_dir_re.match( inp_dir )
    year = inp_dir_m.group( 'year' )
    cik = inp_dir_m.group( 'cik' )
    
    if year < '2006' : continue
    ( cik_to_inp_dirs_nf if cik_to_fy[ cik ] == 'NA' else cik_to_inp_dirs_f )[ cik ].append( inp_dir )


cik_to_inp_dirs = cik_to_inp_dirs_nf
#cik_to_inp_dirs = cik_to_inp_dirs_f

cik_to_year_to_paras_1A = { }
cik_to_year_to_paras_7 = { }

for cik , inp_dirs in cik_to_inp_dirs.items( )[ : 60 ] :
    
    inp_dirs_1A = [ inp_dir for inp_dir in inp_dirs if os.path.isfile( base_inp_dir + '/' + inp_dir + '/1A.txt' ) and os.path.getsize( base_inp_dir + '/' + inp_dir + '/1A.txt' ) > 500 ]
    inp_dirs_7 = [ inp_dir for inp_dir in inp_dirs if os.path.isfile( base_inp_dir + '/' + inp_dir + '/7.txt' ) and os.path.getsize( base_inp_dir + '/' + inp_dir + '/7.txt' ) > 5000 ]
    inp_dirs = sorted( set( inp_dirs_1A ) & set( inp_dirs_7 ) )
    
    if len( inp_dirs ) > 4 :
        cik_to_inp_dirs[ cik ] = inp_dirs
        cik_to_year_to_paras_1A[ cik ] = dict( [ ( inp_dir_re.match( inp_dir ).group( 'year' ) , get_paras( base_inp_dir + '/' + inp_dir + '/1A.txt' ) ) for inp_dir in inp_dirs ] )
        cik_to_year_to_paras_7[ cik ] = dict( [ ( inp_dir_re.match( inp_dir ).group( 'year' ) , get_paras( base_inp_dir + '/' + inp_dir + '/7.txt' ) ) for inp_dir in inp_dirs ] )
    else :
        del cik_to_inp_dirs[ cik ]


#vectorizer = CountVectorizer( min_df = 1 )

def get_matches_by_pc( paras1 , paras2 ) :
    
    matches_by_pc = defaultdict( list )
    for pc in [ 100 , 90 , 80 , 70 , 0 ] :
        matches_by_pc[ pc ]
    
    while True :
    
        len_paras1 = len( paras1 )
        len_paras2 = len( paras2 )    
        
        diff = differ.compare( paras1 , paras2 )
        matches = [ m for m in diff ]
        
        i = 0
        while i < len( matches ) :
            if matches[ i ].startswith( '  ' ) :
                matches_by_pc[ 100 ].append( matches[ i ][ 2 : ] )
                matches[ i : i + 1 ] = [ ]
                continue
            elif matches[ i ].startswith( '? ' ) :
                if matches[ i - 1 ].startswith( '+ ' ) :
                    s = difflib.SequenceMatcher( None , matches[ i - 2 ][ 2 : ] , matches[ i - 1 ][ 2 : ] )
                    matches_by_pc[ int( s.ratio( ) * 10 ) * 10 ] += [ matches[ i - 2 ] , matches[ i - 1 ] ]
                    matches[ i - 2 : i + 1 ] = [ ]
                    i = i - 2
                else :
                    s = difflib.SequenceMatcher( None , matches[ i - 1 ][ 2 : ] , matches[ i + 1 ][ 2 : ] )
                    matches_by_pc[ int( s.ratio( ) * 10 ) * 10 ] += [ matches[ i - 1 ] , matches[ i + 1 ] ]
                    matches[ i - 1 : ( i + 3 if i + 2 < len( matches ) and matches[ i + 2 ].startswith( '? ' ) else i + 2 ) ] = [ ]
                    i = i - 1
                continue
            i += 1
        
        paras1 = [ para[ 2 : ] for para in matches if para.startswith( '- ' ) ]
        paras2 = [ para[ 2 : ] for para in matches if para.startswith( '+ ' ) ]
        
        if len( paras1 ) == len_paras1 and len( paras2 ) == len_paras2 :
            break

    matches_by_pc[ 0 ] = matches
    return matches_by_pc
    
    


for cik , year_to_paras in cik_to_year_to_paras_1A.items( )[ 0 : 5 ] :
    
    print cik
    #print '{} : failed {}'.format( cik , cik_to_fy[ cik ] )
    
    years = sorted( year_to_paras )
    
    for y in range( len( years ) - 1 )[ 0 : ] :
        
        paras1 = year_to_paras[ years[ y ] ]
        paras2 = year_to_paras[ years[ y + 1 ] ]
        
        matches_by_pc = get_matches_by_pc( paras1 , paras2 )
        
        pcs = sorted( matches_by_pc , reverse = True )
        
        num_paras_list = [ len( matches_by_pc[ pc ] ) * ( 2 if pc == 100 else 1 ) for pc in pcs ]
        total_num_paras = float( sum( num_paras_list ) )
        num_paras_pc_list = [ int( num_paras / total_num_paras * 100 ) for num_paras in num_paras_list ]
        
        unchanged_sent_counts_list = [ np.sum( [ mast_dict[ word ]
                                           for word in 
                                           [ stemmer.stem( word.lower( ) ) for para in matches_by_pc[ pc ] for word in para.split( ) ] 
                                           if word in mast_dict ] ,
                                         axis = 0 ) / float( sum( [ 1 for para in matches_by_pc[ pc ] for word in para.split( ) ] ) )
                                 if matches_by_pc[ pc ] else np.zeros( 4 )
                                 for pc in pcs[ : 1 ] ]
        unchanged_sent_counts_list = [ ( sent_counts * 100 ).astype( int ).tolist( ) for sent_counts in unchanged_sent_counts_list ]        
        
        old_sent_counts_list = [ np.sum( [ mast_dict[ word ]
                                           for word in 
                                           [ stemmer.stem( word.lower( ) ) for para in matches_by_pc[ pc ] if para.startswith( '- ' ) for word in para.split( ) ] 
                                           if word in mast_dict ] ,
                                         axis = 0 ) / float( sum( [ 1 for para in matches_by_pc[ pc ] if para.startswith( '- ' ) for word in para.split( ) ] ) )
                                 if matches_by_pc[ pc ] else np.zeros( 4 )
                                 for pc in pcs[ 1 : ] ]
        old_sent_counts_list = [ ( sent_counts * 100 ).astype( int ).tolist( ) for sent_counts in old_sent_counts_list ]
        
        new_sent_counts_list = [ np.sum( [ mast_dict[ word ]
                                           for word in 
                                           [ stemmer.stem( word.lower( ) ) for para in matches_by_pc[ pc ] if para.startswith( '+ ' ) for word in para.split( ) ] 
                                           if word in mast_dict ] ,
                                         axis = 0 ) / float( sum( [ 1 for para in matches_by_pc[ pc ] if para.startswith( '+ ' ) for word in para.split( ) ] ) )
                                 if matches_by_pc[ pc ] else np.zeros( 4 )
                                 for pc in pcs ]
        new_sent_counts_list = [ ( sent_counts * 100 ).astype( int ).tolist( ) for sent_counts in new_sent_counts_list[ 1 : ] ]        
        
        print years[ y ] , years[ y + 1 ] , ':' , zip( pcs , num_paras_pc_list , unchanged_sent_counts_list + old_sent_counts_list , unchanged_sent_counts_list + new_sent_counts_list )
    
    print
    '''
    for pc in sorted( matches_by_pc , reverse = True ) :
        print pc
        for x in matches_by_pc[ pc ] : print x
        print
    '''
