import os
import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer

from sklearn.preprocessing import normalize
from scipy.stats import entropy
from astropy.table import Table


base_inp_dir = 'forms_int_rep_wordlist_filtered'
out_path = 'wordlist_stats.txt'

vectorizer = CountVectorizer(min_df=1)

inp_file_re = re.compile( r'(?P<cik>\d+)_(?P<yyyy>\d{4})-(?P<mm>\d{2})-(?P<dd>\d{2}).txt' )


corpus = [ ]

sics = sorted( os.listdir( base_inp_dir ) )
sic_to_ciks = defaultdict( set )
ciks = set( )
cik_to_inp_files = defaultdict( list )
sic_to_inp_files = defaultdict( list )
inp_files = [ ]
inp_file_to_doc_index = { }

for sic in sics :
    
    for inp_file in os.listdir( base_inp_dir + '/' + sic ) :
        
        inp_file_m = inp_file_re.match( inp_file )
        cik = inp_file_m.group( 'cik' )
        sic_to_ciks[ sic ].add( cik )
        ciks.add( cik )
        cik_to_inp_files[ cik ].append( inp_file )
        sic_to_inp_files[ sic ].append( inp_file )
        inp_files.append( inp_file )
    
        inp = open( base_inp_dir + '/' + sic + '/' + inp_file )
        text = inp.read( )
        inp.close( )
        
        inp_file_to_doc_index[ inp_file ] = len( corpus )
        corpus.append( text )
        
        
doc_word_mat = vectorizer.fit_transform( corpus )
doc_word_mat = np.asarray( doc_word_mat.todense( ) )

words = [ str( word ) for word in vectorizer.get_feature_names( ) ]

sic_word_mat = np.empty( ( len( sics ) , len( words ) ) , dtype = object )
for row in range( len( sics ) ) :
    for col in range( len( words ) ) :
        sic_word_mat[ row , col ] = [ ]

for row , sic in enumerate( sics ) :    
    for inp_file in sic_to_inp_files[ sic ] :
        for col in range( len( words ) ) :
            sic_word_mat[ row , col ].append( doc_word_mat[ inp_file_to_doc_index[ inp_file ] , col ] )

word_indices = range( len( words ) )
#for word in [ 'arbitrage' , 'call_option' ,  'put_option' , 'risk_mitigation' , 'risk_transfer' , 'uncleared' ] :
#    word_indices.remove( words.index( word ) )

    
sic_colors = [ 'fuchsia', 'aqua', 'olivedrab' , 'gold' ]

num_displayed = 4
index_offset = 0

while index_offset < len( word_indices ) - 1 :

    fig, axes = plt.subplots( nrows = 2 , ncols = 2 )
    axes_array = axes.flatten()
    
    for i in range( len( word_indices ) - index_offset )[ : num_displayed ] :
        axes_array[ i ].hist( [ sic_word_mat[ row , word_indices[ i + index_offset ] ] for row in range( len( sics ) ) ] , 
                              25 , histtype = 'bar' , color = sic_colors , label = sics , stacked = True , edgecolor = 'black' , linewidth = .2 , range = ( 0 , 250 ) )
        axes_array[ i ].set_title( words[ word_indices[ i + index_offset ] ] )
        axes_array[ i ].legend( prop = { 'size' : 10 } )
        axes_array[ i ].set_xlabel( 'firm-year word count' )
        axes_array[ i ].set_ylabel( 'frequency' )
        
    fig.tight_layout()
    
    index_offset += num_displayed


sic_word_sum_mat = np.empty( ( len( sics ) , len( words ) ) , dtype = int )
for row in range( len( sics ) ) :
    for col in range( len( words ) ) :
        sic_word_sum_mat[ row , col ] = sum( sic_word_mat[ row , col ] )


proto_row = [ '-' for yyyy in range( 2006 , 2017 ) ]
        
p_mat = doc_word_mat[ : , word_indices ] + 0.00000001
p_mat = normalize( p_mat , norm = 'l1' )

table_rows = [ ]
sic_to_table_rows = defaultdict( list )
table_header = [ str( yyyy ) for yyyy in range( 2006 , 2017 ) ]

for sic in sorted( sic_to_ciks ) :
    
    for cik in sorted( sic_to_ciks[ sic ] ) :
        
        cik_inp_files = cik_to_inp_files[ cik ]
        
        table_row = proto_row[ : ]
        
        for i in range( len( cik_inp_files ) - 1 ) :
            
            inp_file1 = cik_inp_files[ i ]
            inp_file2 = cik_inp_files[ i + 1 ]
            
            yyyy1 = inp_file_re.match( inp_file1 ).group( 'yyyy' )
            yyyy2 = inp_file_re.match( inp_file2 ).group( 'yyyy' )
            if yyyy1 == yyyy2 :
                yyyy2 = str( int( yyyy1 ) + 1 ) 
            
            q = p_mat[ inp_file_to_doc_index[ inp_file1 ] ]
            p = p_mat[ inp_file_to_doc_index[ inp_file2 ] ]
            kl_div = round( entropy( p , q ) , 2 )
            
            table_row[ int( yyyy2 ) - 2006 ] = str( kl_div )
        
        sic_to_table_rows[ sic ].append( [ cik , sic ] + table_row )
    
    mean_row = [ round( np.mean( [ float( kl_div ) for kl_div in [ row[ yyyy - 2006 + 2 ] for row in sic_to_table_rows[ sic ] ] if kl_div != '-' ] ) , 2 ) for yyyy in range( 2006 , 2017 ) ]
    sic_to_table_rows[ sic ].append( [ 'average' , sic ] + mean_row )

    table_rows += sic_to_table_rows[ sic ] + [ [ ' ' ] * ( 2 + len( proto_row ) ) ]

table = Table( rows = table_rows , names = tuple( [ 'cik' , 'sic' ] + table_header ) )

'''
fig, axes = plt.subplots( nrows = 1 , ncols = 1 )

for table_row in table_rows :
    if table_row[ 0 ] == ' ' :
        continue
    sic = table_row[ 1 ]
    data = [ ( 2006 + i , float( kl_div ) ) for i , kl_div in enumerate( table_row[ 2 : ] ) if kl_div != '-' ]
    data = zip( *data )
    if not data :
        continue
    axes.plot( data[ 0 ] , data [ 1 ] , color = sic_colors[ sics.index( sic ) ] )

fig.tight_layout()
'''

sic_to_desc = { '6200' : 'SECURITY & COMMODITY BROKERS, DEALERS, EXCHANGES & SERVICES' ,
                '6211' : 'SECURITY BROKERS, DEALERS & FLOTATION COMPANIES' ,
                '6221' : 'COMMODITY CONTRACTS BROKERS & DEALERS' ,
                '6282' : 'INVESTMENT ADVICE' }

out = open( out_path , 'w' )

out.write( 'Summary statistics of 10-Ks\n' )
out.write( '===========================\n' )
out.write( 'sic   #firms  #firm-years  description\n' )
out.write( '----  ------  -----------  -----------\n' )
for sic in sics :
    out.write( '{}  {}  {}  {}\n'.format( sic , str( len( sic_to_ciks[ sic ] ) ).rjust( 6 ) , str( len( sic_to_inp_files[ sic ] ) ).rjust( 11 ) , sic_to_desc[ sic ] ) )
out.write( '----  -----  -----\n' )
out.write( 'total {}  {}\n\n\n'.format( str( len( ciks ) ).rjust( 6 ) , str( len( inp_files ) ).rjust( 11 ) ) )

out.write( 'Aggregate word counts over all firm-years\n' )
out.write( '=========================================\n' )
out.write( 'sic   ' + '  '.join( [ words[ i ] for i in word_indices ] ) + '\n' )
out.write( '----  ' + '  '.join( [ '-' * len( words[ i ] ) for i in word_indices ] ) + '\n' )
for row , sic in enumerate( sics ) :
    out.write( sic + '  ' + '  '.join( [ str( sic_word_sum_mat[ row , i ] ).rjust( len( words[ i ] ) ) for i in word_indices ] ) + '\n' )
out.write( '----  ' + '  '.join( [ '-' * len( words[ i ] ) for i in word_indices ] ) + '\n' )
out.write( 'total ' + '  '.join( [ str( sum( [ sic_word_sum_mat[ row , i ] for row in range( len( sics ) ) ] ) ).rjust( len( words[ i ] ) ) for i in word_indices ] ) + '\n\n\n' )

out.write( 'Per firm-year word counts over all firm-years\n' )
out.write( '=============================================\n' )
out.write( 'sic   ' + '  '.join( [ words[ i ] for i in word_indices ] ) + '\n' )
out.write( '----  ' + '  '.join( [ '-' * len( words[ i ] ) for i in word_indices ] ) + '\n' )
for row , sic in enumerate( sics ) :
    out.write( sic + '  ' + '  '.join( [ '{:.1f}'.format( sic_word_sum_mat[ row , i ] / float( len( sic_to_inp_files[ sic ] ) ) ).rjust( len( words[ i ] ) ) for i in word_indices ] ) + '\n' )
out.write( '      ' + '  '.join( [ '-' * len( words[ i ] ) for i in word_indices ] ) + '\n' )
out.write( '      ' + '  '.join( [ '{:.1f}'.format( sum( [ sic_word_sum_mat[ row , i ] for row , sic in enumerate( sics ) ] ) / float( len( inp_files ) ) ).rjust( len( words[ i ] ) ) for i in word_indices ] ) + '\n\n\n' )

out.write( 'KL-divergence from previous firm-year\'s data for given firm\n' )
out.write( '============================================================\n')
out.write( str( table[ 0 ] ) + '\n' )
for i in range( 1 , len( table ) ) :
    out.write( str( table[ i ] ).split( '\n' , 2 )[ -1 ] + '\n' )
out.write( '\n\n' )

out.close( )



'''
top_word_indices = [ X_sum.argsort( )[ : : -1 ][ i ] for i in range( 20 ) ]
top_words = [ ( str( words[ i ] ) , '{:.1e}'.format( X_sum[ i ] / X.shape[ 0 ] , 2 ) ) for i in top_word_indices ]
print top_words

for sic in sorted( sic_to_X_sum ) :
    top_word_indices = [ sic_to_X_sum[ sic ].argsort( )[ : : -1 ][ i ] for i in range( 20 ) ]
    top_words = [ ( str( words[ i ] ) , '{:.1e}'.format( sic_to_X_sum[ sic ][ i ] / len( sic_to_X_sum[ sic ] ) ) ) for i in top_word_indices ]
    print sic, top_words'''