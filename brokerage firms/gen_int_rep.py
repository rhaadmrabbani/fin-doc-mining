import os , os.path
import re
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


base_inp_dir = 'forms'
base_out_dir = 'forms_int_rep'

stemmer = PorterStemmer( )
stop_words = set( [ stemmer.stem( word.lower( ) ) for word in stopwords.words( 'english' ) ] )


doc_re = re.compile( r'<document>(?P<doc>.*?)</document>' , re.I | re.S )
doc_type_re = re.compile( r'<type>(?P<type>.*?)\n' , re.I )
doc_text_re = re.compile( r'<text>(?P<text>.*?)</text>' , re.I | re.S )
doc_pdf_re = re.compile( r'<pdf>.*?</pdf>' , re.I | re.S )

tag_re = re.compile( r'<.*?>' , re.S )
sp_char_re = re.compile( r'&[^ ]*;' )
word_re = re.compile( r'[a-z]{2,}|[\.\?,:;\'"\n]' , re.I )


for sic in os.listdir( base_inp_dir ) :
    
    inp_files = os.listdir( base_inp_dir + '/' + sic )
    print sic , len( inp_files )
    
    if not os.path.isdir( base_out_dir + '/' + sic ) :
        os.makedirs( base_out_dir + '/' + sic )
    
    for inp_file in inp_files :
        
        inp = open( base_inp_dir + '/' + sic + '/' + inp_file )
        text = inp.read( )
        inp.close( )
        
        for doc_m in doc_re.finditer( text ) :            
            doc = doc_m.group( 'doc' )
            doc_type = doc_type_re.search( doc ).group( 'type' ).strip( )    
            if doc_type != '10-K' : continue    
            doc_text = doc_text_re.search( doc ).group( 'text' )    
            if doc_pdf_re.search( doc_text ) : continue
            text = doc_text
            break
        
        text = tag_re.sub( '' , text )
        text = sp_char_re.sub( ' ' , text )
        words = [ word for word in [ m.group( ).lower( ) for m in word_re.finditer( text ) ] if not stemmer.stem( word ) in stop_words ]
        text = ' '.join( words )
        
        out = open( base_out_dir + '/' + sic + '/' + inp_file , 'w' )
        out.write( text )
        out.close( )

