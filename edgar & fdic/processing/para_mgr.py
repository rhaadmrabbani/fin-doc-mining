import re



start_tag = r'(\s*<[^/>]*>\s*)'
end_tag = r'(\s*</[^>]*>\s*)'

junk = r'(\s|<[^>]*>)*'

page_num_rs = '(F *- *)?\d+'


table_start_re = re.compile( r'^\s*<table>\s*$' , re.I )
table_end_re = re.compile( r'^\s*</table>\s*$' , re.I )

gunk_re = re.compile( r'^{0}\??{0}$'.format( junk ) , re.S )
false_gunk_re = re.compile( r'</?table>|<page>' , re.I )

tag_re = re.compile( r'<[^>]*>' , re.S )



class Para :
    
    def __init__( self , text , inside_table = False ) :
        
        self.text = text
        self.inside_table = inside_table



para_re = re.compile( r'(^|(?<=\n\n)).*?\n(?=\n|$)' , re.S )


def get_paras( doc ) :
    
    paras = [ Para( para_m.group( ) ) for para_m in para_re.finditer( doc.doc_text ) ]
    paras = process_tables( paras )
    paras = preprocess_text( paras )
    paras = process_page_seps( paras )
    paras = postprocess_page_seps( paras )
    paras = process_titles( paras )
    paras = postprocess_text( paras )
    
    return paras



def process_tables( paras ) :
    
    inside_table = False
    i = 0
    while i < len( paras ) :
        if table_start_re.match( paras[ i ].text ) :
            inside_table = True       
        elif table_end_re.match( paras[ i ].text ) :
            inside_table = False
        else :
            paras[ i ].inside_table = inside_table
        i += 1    
    
    return paras




item_re = re.compile( r'(^|(?<=\n)){0}i{0}t{0}e{0}ms?(\W|$)'.format( junk ) , re.I )
part_re = re.compile( r'(^|(?<=\n)){0}part(\W|$)'.format( junk ) , re.I )
hdr_re = re.compile( r'(^|(?<=\n)){0}((part{0}(\S+?{0}){{1,2}})?i{0}t{0}e{0}ms?(\W|$)|part(\W|$)|signature)'.format( junk ) , re.I )


def preprocess_text( paras ) :
    
    i = 0
    while i < len( paras ) :
        if gunk_re.match( paras[ i ].text ) and not false_gunk_re.search( paras[ i ].text ) :
            paras[ i : i + 1 ] = [ ]
            continue        
        elif hdr_re.match( paras[ i ].text ) or ( item_re.search( paras[ i ].text ) and part_re.search( paras[ i ].text ) ):
            hdr_m_starts = [ hdr_m.start( ) for hdr_m in hdr_re.finditer( paras[ i ].text ) ]
            sub_para_texts = [ paras[ i ].text[ start : end ].strip( '\n' ) for start , end in zip( [ 0 ] + hdr_m_starts , hdr_m_starts + [ len( paras[ i ].text ) ] ) ]
            sub_paras = [ Para( sub_para_text + '\n' , inside_table = paras[ i ].inside_table ) for sub_para_text in sub_para_texts if sub_para_text ]
            paras[ i : i + 1 ] = sub_paras
            i += len( sub_paras )
            continue
        i += 1
        
    return paras



page_num_re = re.compile( r'^('
                          + r'{0}(-\s*)?(?P<num1>{1})\.?(\s*-)?({0}|(?P<nextpage>{0}?next\s+page{0}))'.format( junk , page_num_rs )
                          + r'|{0}[^<>]*(-{1}|{1}- *)(?P<num2a>{2})\s*'.format( start_tag , end_tag , page_num_rs )
                          + r'|\s*(?P<num2b>{2})( *-{0}|{0}-)[^<>]*{1}'.format( start_tag , end_tag , page_num_rs )
                          + r')$' , re.I | re.S )
ending_page_num_re = re.compile( r'(?<=\n)\s*(-\s*)?(?P<num1>{0})(\s*-)?\s*$'.format( page_num_rs ) , re.S )

page_sep_re = re.compile( r'^{0}?(table\s+of\s+contents|<page>){0}$'.format( junk ) , re.I | re.S )


def process_page_seps( paras ) :
    
    i = 0
    while i + 1 < len( paras ) :
        m = page_num_re.match( paras[ i ].text )
        ending_m = ending_page_num_re.search( paras[ i ].text )
        if m :            
            page_sep_para = Para( '<page> {0}\n'.format( m.group( 'num1' ) or m.group( 'num2a' ) or m.group( 'num2b' ) ) )
            if i > 0 and i + 1 < len( paras ) and table_start_re.match( paras[ i - 1 ].text ) and table_end_re.match( paras[ i + 1 ].text ) :
                paras[ i - 1 : i + 2 ] = [ page_sep_para ] 
                continue
            elif page_sep_re.match( paras[ i + 1 ].text ) :
                sub_paras = [ Para( '</table>' ) , page_sep_para , Para( '<table>' ) ] if paras[ i ].inside_table else [ page_sep_para ]
                paras[ i : i + 2 ] = sub_paras
                i += len( sub_paras )
                continue
            elif i + 2 < len( paras ) and table_end_re.match( paras[ i + 1 ].text ) and page_sep_re.match( paras[ i + 2 ].text ) :
                paras[ i : i + 3 ] = [ paras[ i + 1 ] , page_sep_para ]
                i += 2
                continue
            elif not paras[ i ].inside_table and m.group( 'nextpage' ) :
                paras[ i ] = page_sep_para
        elif ending_m :
            if page_sep_re.match( paras[ i + 1 ].text ) :
                paras[ i : i + 1 ] = [ Para( paras[ i ].text[ : ending_m.start( ) ] , inside_table = paras[ i ].inside_table ) ,
                                       Para( paras[ i ].text[ ending_m.start( ) : ] , inside_table = paras[ i ].inside_table ) ]
        i += 1
    
    return paras



pre_page_sep_re = re.compile( r'[\w,;]{0}$'.format( junk ) , re.S )
page_sep_re2 = re.compile( r'^{0}?<page>{0}{1}{0}$'.format( junk , page_num_rs ) , re.I | re.S )
bad_post_page_sep_re = re.compile( r'^{0}(items?(\W|$)|part(\W|$)|signature)'.format( junk ) , re.I | re.S )


def postprocess_page_seps( paras ) :
    
    i = 0
    while i + 2 < len( paras ) :
        if not page_sep_re2.match( paras[ i ].text ) and pre_page_sep_re.search( paras[ i ].text ) and page_sep_re2.match( paras[ i + 1 ].text ) and not bad_post_page_sep_re.search( paras[ i + 2 ].text ) :
            paras[ i ].text += ' ' + paras[ i + 2 ].text
            paras[ i + 2 : i + 3 ] = [ ]
            i += 2
            continue
        i += 1
    
    return paras



title_re = re.compile( r'^(?P<pre> *)(?P<title>(({0}[^<>]*{1}|{0}[^<>]*{0}[^<>]*{1}[^<>]*{1})[^<>\w]*)+)(?P<post>(\w.*)?)$'.format( start_tag , end_tag ) , re.S )

def process_titles( paras ) :
    
    i = 0
    while i < len( paras ) :
        title_m = title_re.match( paras[ i ].text )
        if title_m and title_m.group( 'post' ) :
            paras[ i : i + 1 ] = [ Para( ( title_m.group( 'pre' ) + title_m.group( 'title' ) ).strip( '\n' ) + '\n' , inside_table = paras[ i ].inside_table ) ,
                                   Para( title_m.group( 'pre' ) + title_m.group( 'post' ) , inside_table = paras[ i ].inside_table ) ]
            i += 2
            continue
        i += 1
  
    return paras    



title_re2 = re.compile( r'^(?P<pre> *)(?P<title>(({0}[^<>]*{1}|{0}[^<>]*{0}[^<>]*{1}[^<>]*{1})[^<>\w]*)+)\n$'.format( start_tag , end_tag ) , re.S )


def postprocess_text( paras ) :
    
    i = 0
    while i < len( paras ) :
        if i + 1 < len( paras ) and table_end_re.match( paras[ i ].text ) and table_start_re.match( paras[ i + 1 ].text ) :
            paras[ i: i + 2 ] = [ ]
            continue
        else :
            paras[ i ].text = flatten_para_text( paras[ i ].text )
            title_m = title_re2.match( paras[ i ].text )
            if title_m :
                paras[ i ].text = '{0}<h>{1}</h>\n'.format( title_m.group( 'pre' ) , tag_re.sub( '' , title_m.group( 'title' ) ) )            
        i += 1
        
    return paras



line_re = re.compile(  r'(^|(?<=\n))(?P<pre> *)(?P<body>.*?) *(?=\n)' ) 


def flatten_para_text( para_text ) :
    
    line_ms = [ line_m for line_m in line_re.finditer( para_text ) ]
    
    num = len( line_ms )
    if num <= 1 : return para_text

    pre_lens = [ len( line_m.group( 'pre' ) ) for line_m in line_ms ]

    if 1:#pre_lens[ 0 ] + 2 >= sorted( pre_lens[ 1 : ] )[ num / 2 - 1 ] :
        
        lines = [ line_m.group( 'body' ) for line_m in line_ms ]
        para_text = line_ms[ 0 ].group( 'pre' ) + ' '.join( lines ) + '\n'
    
    return para_text
