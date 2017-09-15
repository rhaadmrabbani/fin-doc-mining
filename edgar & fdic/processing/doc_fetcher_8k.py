import re



class Doc :
    
    def __init__( self , doc_type , doc_text ) :
        self.doc_type = doc_type
        self.doc_text = doc_text



doc_re = re.compile( r'<document>(?P<doc>.*?)</document>' , re.I | re.S )
doc_type_re = re.compile( r'<type>(?P<type>.*?)\n' , re.I )
doc_text_re = re.compile( r'<text>(?P<text>.*?)</text>' , re.I | re.S )
doc_pdf_re = re.compile( r'<pdf>.*?</pdf>' , re.I | re.S )


def fetch_docs( text ) :
    
    docs = [ ]
    
    for doc_m in doc_re.finditer( text ) :
        
        doc = doc_m.group( 'doc' )
        doc_type = doc_type_re.search( doc ).group( 'type' ).strip( )    
        if doc_type != '8-K' : continue    
        doc_text = doc_text_re.search( doc ).group( 'text' )    
        if doc_pdf_re.search( doc_text ) : continue
        doc_text = preprocess( doc_text )
        doc = Doc( doc_type , doc_text )
    
        docs.append( doc )
    
    return docs



cr_re = re.compile( r'\r' )
tab_re = re.compile( r'\t' )
tag_re = re.compile( r'<(?P<label>/?\w+)(\s[^>]*)?>' , re.S )

sp_char_re = re.compile( r'&(?P<code>.{1,6}?);' , re.S )
sp_char_map = dict( [ ( k , v ) for ks , v in [ ( [ 'nbsp' , '#160' , '#9' , '#09' , '#009' ] , ' ' ) ,
                                                ( [ 'amp' , '#38' , '#038' ] , ' & ' ) ,
                                                ( [ '#43' , '#043' ] , ' + ' ) ,
                                                ( [ 'lt' , '#60' , '#060' ] , '<' ) ,
                                                ( [ 'gt' , '#62' , '#062' ] , '>' ) ,
                                                ( [ '#91' , '#091' ] , ' [ ' ) ,
                                                ( [ '#93' , '#093' ] , ' ] ' ) ,
                                                ( [ '#95' , '#095' ] , '_' ) ,
                                                ( [ '&rsquo' , '#145' , '#146' , '#8216' , '#8217' ] , "'" ) ,
                                                ( [ '&ldquo' , '&rdquo' ,  'quot' , '#147' , '#148' , '#8220' , '#8221' ] , '"' ) ,
                                                ( [ '#150' , '#151' , '#8212' ] , ' - ' ) ] for k in ks ] )

caps_font_tag_re = re.compile( r'(?P<pre><font[^<>]*text-transform: uppercase[^<>]*>)(?P<text>.*?)(?P<post></font>)' , re.I | re.S )
keep_font_tag_re = re.compile( r'<font[^<>]*(bold|italic|underline)[^<>]*>(?P<text>.*?)</font>' , re.I | re.S )
nl_div_tag_re = re.compile( r'<div[^<>]*(margin|padding)-(top|bottom)[^<>*]*>.*?(</div>|(?=<p[ >])|(?=<table))' , re.I | re.S )
discard_tag_re = re.compile( r'</?(a|font)>|<!--[^>]*-->' , re.I | re.S )
discard_spc_tag_re = re.compile( r'</?(html|head|title|body|td|th|div)>|<!--[^>]*-->' , re.I | re.S )
keep_nl_tag_re = re.compile( r'</?table>|<page>.*?(?=\n)' , re.I )
discard_nl_tag_re = re.compile( r'((</?(br|hr|tr|p|ul|li)>) *)+' , re.I )
gunk_re = re.compile( r'<(?P<tag>[^/>]*)>(?P<text>\s*)</(?P=tag)>|</(?P<tag2>[^/>]*)>(?P<text2>\s*)<(?P=tag2)>' , re.I )
multi_nl_re = re.compile( r'\n\s*\n' )
multi_spc_re = re.compile( r' {2,}' )

def preprocess( text ) :
    
    text = cr_re.sub( '' , text )
    text = tab_re.sub( ' ' , text )
    text = caps_font_tag_re.sub( lambda m : m.group( 'pre' ) + m.group( 'text' ).upper( ) + m.group( 'post' ) , text )
    text = keep_font_tag_re.sub( r'<h>\g<text></h>' , text )
    text = nl_div_tag_re.sub( r'\n\n\g<0>\n\n' , text )
    text = tag_re.sub( r'<\g<label>>' , text )
    text = sp_char_re.sub( lambda m : sp_char_map[ m.group( 'code' ) ] if m.group( 'code' ) in sp_char_map else '?' , text )
    text = discard_tag_re.sub( '' , text )
    text = discard_spc_tag_re.sub( ' ' , text )
    text = keep_nl_tag_re.sub( r'\n\n\g<0>\n\n' , text )
    text = discard_nl_tag_re.sub( '\n\n' , text )
    text = gunk_re.sub( lambda m : m.group( 'text' ) or m.group( 'text2' ) , text )
    text = gunk_re.sub( lambda m : m.group( 'text' ) or m.group( 'text2' ) , text )
    text = multi_nl_re.sub( '\n\n' , text )
    text = multi_spc_re.sub( '  ' , text )    
    
    text = text.strip( '\n' )
    if text :
        return text + '\n'