import re

from collections import defaultdict
from os import listdir, makedirs
from os.path import isdir

from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

pos_map = { 'NN' : 'n', 'VB' : 'v', 'RB' : 'r', 'JJ' : 'a' }
wordnet_lemmatizer = WordNetLemmatizer()
filter_part = lambda words: [ wordnet_lemmatizer.lemmatize(word, pos=pos_map[pos[:2]]) if pos[:2] in pos_map else word for word, pos in pos_tag(words) ]


items = defaultdict(list)


inp_dirpath = 'sections/8-K'
out_dirpath = 'multifiltered_sections/8-K'


def main( ) :
    opendir( '' )


def opendir( dirpath_suff ) :
    
    print inp_dirpath + dirpath_suff
    if not isdir( out_dirpath + dirpath_suff ) :
        makedirs( out_dirpath + dirpath_suff )
    
    filenames = listdir( inp_dirpath + dirpath_suff )
    filenames.sort( )
   
    for filename in filenames :
        if isdir( inp_dirpath + dirpath_suff + '/' + filename ) :
            opendir( dirpath_suff + '/' + filename )
        #elif '2000' <= filename < '2020':
        else :
            openfile( dirpath_suff + '/' + filename )


bad_paren_re = re.compile( '\(.\)' )
bad_pos_re = re.compile( r'NNP|IN|DT|C.*|TO|.*RP.*|WDT' )
stop = stopwords.words('english')
non_alpha_re = re.compile( r'[^A-Za-z]' )

def openfile( filepath_suff ) :
    
    print filepath_suff
    inp_file = open( inp_dirpath + filepath_suff, 'r' )
    text = inp_file.read( )
    inp_file.close( )

    text = sent_tokenize(text)
    #text = [ pos_tag( sent.split() ) for sent in text ]
    text = [ [ ( non_alpha_re.sub( '', word ), pos ) for word, pos in pos_tag( sent.split() ) 
               if not bad_pos_re.match( pos ) and not word in stop and not '$' in word and not bad_paren_re.match( word ) ]
             for sent in text ]
    text = [ [ wordnet_lemmatizer.lemmatize(word, pos=pos_map[pos[:2]]) if pos[:2] in pos_map else word for word, pos in sent ] for sent in text ]
    text = '\n\n'.join( [ ' '.join( sent ) for sent in text ] )
    
    
    
    out_file = open( out_dirpath + filepath_suff, 'w' )
    out_file.write( str(text) )
    out_file.close( )
            


def re_split( regexp, m_lambda, non_m_lambda, text ):
    
    ms = [ m for m in regexp.finditer( text ) ]
    m_texts = [ m_lambda( m.group( ) ) for m in ms ]
    
    non_ms = zip( [ 0 ] + [ m.end( ) for m in ms ], [ m.start( ) for m in ms ] + [ len( text ) ] )
    non_m_texts = [ non_m_lambda( text[ s : e ] ) for s, e in non_ms ]
    
    return non_m_texts[ : 1 ] + [ t for ts in zip( m_texts, non_m_texts [ 1 : ] ) for t in ts ]


main( )
#openfile( '/8-K/2012-11-26-860519.txt' )