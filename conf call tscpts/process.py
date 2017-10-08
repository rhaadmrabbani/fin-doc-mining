# MIT License
#
# Copyright (c) 2017 Rhaad M. Rabbani
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



# PDF parsing code obtained from pdfminer 0.0.1 docs (Sep 17, 2017) by Yusuke Shinyama
# https://media.readthedocs.org/pdf/pdfminer-docs/latest/pdfminer-docs.pdf

# pdfminer donloaded from https://github.com/euske/pdfminer



data_dir = 'in'
intermediate_rep_out_dir = 'ir_out'
out_dir = 'out'


import os
import os.path
import re

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage , PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager , PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams , LTTextBoxHorizontal , LTChar
from pdfminer.converter import PDFPageAggregator



class Para :
    
    def __init__( self , lines ) :
        lines = [ line.strip( ) for line in lines ]
        lines = [ line for line in lines if line ]
        self.lines = lines
        
        
        
class Page :
    
    def __init__( self , paras ) :
        self.headers = { }
        self.paras = paras
        self.footers = { }
        
    def __repr__( self ) :
        text = ''
        if self.headers :
            for header_type , header in self.headers.iteritems( ) :
                text += ''.join( [ '[ ' + line + ' ]\n' for line in header.lines ] ) + '\n'
        for para in self.paras :
            text += ''.join( [ line + '\n' for line in para.lines ] ) + '\n'
        if self.footers :
            for footer_type , footer in self.footers.iteritems( ) :
                text += ''.join( [ '[ ' + line + ' ]\n' for line in footer.lines ] ) + '\n'
        text += ( '*' * 40 ) + '\n\n'
        return text



bold_re = re.compile( 'bold' , re.I )

def pdf_to_pages( file_path ) :

    document = open( file_path , 'rb' )
    res_mgr = PDFResourceManager( )
    device = PDFPageAggregator( res_mgr , laparams = LAParams( ) )
    interpreter = PDFPageInterpreter( res_mgr , device )
    
    pages = [ ]
    
    for page in PDFPage.get_pages( document ) :
        
        interpreter.process_page( page )
        fontname_to_bold = dict( [ ( font.basefont , bold_re.search( font.basefont ) != None ) for font in interpreter.fontmap.values( ) ] )
        layout = device.get_result( )
        paras = [ ]
        
        for element in layout :
            if isinstance( element , LTTextBoxHorizontal ) :
                lines = element._objs
                for i , line in enumerate( lines ) :
                    lines[ i ] = ''.join( [ c.get_text( ).encode('utf-8').upper( )
                                            if isinstance( c , LTChar ) and ( fontname_to_bold[ c.fontname ] or 17.20880205278 < c.size < 17.20880205279 )
                                            else c.get_text( ).encode('utf-8') for c in line._objs ] ).replace( '\xc2\xa0' , ' ' ).replace( '\xe2\x80\x93' , '-' ).replace( '\xc2\xad' , '-' )
                paras.append( Para( lines ) )
                
        paras = [ para for para in paras if para.lines ]
        pages.append( Page( paras ) )
    
    return pages
        


def get_reg_exp_name( reg_exp_dict , text ) :
    for name , reg_exp in reg_exp_dict.iteritems( ) :
        if reg_exp.search( text ) :
            return name



header_res = { }
header_res[ 'seekingalpha_date' ] = re.compile( r'^\d{1,2}/\d{1,2}/\d{2}(\d{2})?$' )
header_res[ 'seekingalpha_title' ] = re.compile( r' \| Seeking Alpha$' )
header_res[ 'reuters_clientid' ] = re.compile( r'^CLIENT ID:' )
header_res[ 'reuters_title' ] = re.compile( r'^(JANUARY |FEBRUARY |MARCH |APRIL |MAY |JUNE |JULY |AUGUST |SEPTEMBER |OCTOBER |NOVEMBER |DECEMBER )\d{2},' )
header_res[ 'thomson_title' ] = re.compile( r'^Q\d \d{4} ' )
header_res[ 'thomson_page' ] = re.compile( r'^Page \d+$' )
header_res[ 'thomson_day' ] = re.compile( r'^(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)$' )

def extract_headers( pages ) :
    
    for page in pages :
        
        for para in page.paras :
            
            found_header = False
            while para.lines :
                header_type = get_reg_exp_name( header_res , para.lines[ 0 ] )
                if header_type :
                    found_header = True
                    page.headers[ header_type ] = Para( [ para.lines.pop( 0 ) ] )
                else :
                    break
            if not found_header :
                break

        page.paras = [ para for para in page.paras if para.lines ]
        
    header_types = set( )
    for page in pages :
        for header_type , header in page.headers.iteritems( ) :
            header_types.add( header_type )
    
    for page in pages[ 1 : ] :
        for header_type in header_types :
            if not header_type in page.headers :
                header_re = header_res[ header_type ]
                for para_i , para in enumerate( page.paras ) :
                    if header_re.search( para.lines[ 0 ] ) :
                        page.headers[ header_type ] = page.paras.pop( para_i )
                        break
        


footer_res = { }
footer_res[ 'page' ] = re.compile( r'^\d+(/\d+)?$' )
footer_res[ 'seekingalpha_link' ] = re.compile( r'^http://seekingalpha.com/article/' )
footer_res[ 'reuters_copyright' ] = re.compile( r'^\xc2\xa9\d{4} Thomson Reuters' )
footer_res[ 'reuters_streetevents' ] = re.compile( r'^THOMSON REUTERS STREETEVENTS \| www\.streetevents\.com \| Contact Us$' )

def extract_footers( pages ) :
    
    for page in pages :    
        while page.paras :
            lastpara = page.paras[ -1 ]
            footer_type = get_reg_exp_name( footer_res , lastpara.lines[ 0 ]  )
            if footer_type :
                page.footers[ footer_type ] = page.paras.pop( -1 )                
            else :
                break
            


split_line_end_re = re.compile( r'[^\.]$' )
split_line_start_re = re.compile( r'^([a-z\d\$]|-- )' )

def mend_split_paras( pages ) :
        
    pages = [ page for page in pages if page.paras ]
    
    i = 0
    while i < len( pages ) - 1 :
        if split_line_end_re.search( pages[ i ].paras[ -1 ].lines[ -1 ] ) and split_line_start_re.search( pages[ i + 1 ].paras[ 0 ].lines[ 0 ] ) :
            pages[ i ].paras[ -1 ].lines += pages[ i + 1 ].paras[ 0 ].lines
            pages[ i + 1 ].paras.pop( 0 )
            if not pages[ i + 1 ].paras :
                pages.pop( i + 1 )
        i += 1
    
    return pages



'''


def parse_text( text ) :
    
    pre_qna = pre_qna_re.search( text ).group( )
    text = pre_qna_re.sub( '' , text )
    text = copyright_re.sub( '' , text ) 
    
    m = speakers_re.search( pre_qna )
    
    if m :
        
        executives_text = m.group( 'executives' )
        analysts_text = m.group( 'analysts' )
        
        executives = [ p.group( 1 ).replace( '\r' , '' ).replace( '\n' , ' ' ).strip( ) for p in participants_re1.finditer( executives_text ) ]
        analysts = [ p.group( 1 ).replace( '\r' , '' ).replace( '\n' , ' ' ).strip( ) for p in participants_re1.finditer(analysts_text ) ]
        
        if not executives and not analysts :
            executives = [ p.group( ).replace( '\xc2\xa0' , ' ' ).replace( '\xe2\x80\x93' , '-' ).replace( '\r' , '' ).replace( '\n' , ' ' ).strip( ) for p in participants_re2.finditer( executives_text ) ]
            analysts = [ p.group( ).replace( '\xc2\xa0' , ' ' ).replace( '\xe2\x80\x93' , '-' ).replace( '\r' , '' ).replace( '\n' , ' ' ).strip( ) for p in participants_re2.finditer(analysts_text ) ]
            
        text = 'Executives:\n' + '\n'.join( executives ) + '\n\nAnalysts:\n' + '\n'.join( analysts ) + '\n\n' + text
    
    return text
'''


pre_qna_re1 = re.compile( r'^(Q U E S T I O N S   A N D   A N S W E R S|QUESTIONS AND ANSWERS|Questions and Answers|QUESTION-AND-ANSWER SESSION)$' )
pre_qna_re2 = re.compile( r'OPERATOR: \(OPERATOR INSTRUCTIONS\)' )

post_qna_re = re.compile( r'^(D I S C L A I M E R|\[Thomson Financial reserves the right|COPYRIGHT POLICY:)' , re.S )

def extract_qna( paras ) :
    
    pre_qna = [ ]
    qna = paras
    post_qna = [ ]
    
    for i , para in enumerate( qna ) :
        if pre_qna_re1.search( para.lines[ 0 ] ) :
            if len( para.lines ) == 1 :
                pre_qna = qna[ : i + 1 ]
                qna = qna[ i + 1 : ]
            else :
                pre_qna = qna[ : i ] + [ Para( [ para.lines.pop( 0 ) ] ) ]
                qna = qna[ i : ]
            break
        elif pre_qna_re2.search( para.lines[ 0 ] ) :
            pre_qna = qna[ : i ]
            qna = qna[ i : ]
            break
        
    for i , para in reversed( list( enumerate( qna ) ) ) :
        if post_qna_re.search( para.lines[ 0 ] ) :
            post_qna = qna[ i : ]
            qna = qna[ : i ]
            break    
        
    return pre_qna , qna , post_qna
    


speakers_re = re.compile( r'\n(C O R P O R A T E   P A R T I C I P A N T S|CORPORATE PARTICIPANTS|Corporate Participants|EXECUTIVES)\n'
                          + r'(?P<executives>.*)'
                          + r'\n(C O N F E R E N C E   C A L L   P A R T I C I P A N T S|CONFERENCE CALL PARTICIPANTS|Conference Call Participants|ANALYSTS)\n'
                          + r'(?P<analysts>.*)'
                          + r'\n(P R E S E N T A T I O N|OVERVIEW|Presentation|OPERATOR)' , re.S )
participants_re1 = re.compile( r'\*\s+([^-\*]*\s+-\s+[^\n\*]*)' )
participants_re2 = re.compile( r'[^\n-]*\s+-\s+[^\n]+' )

def extract_speakers_from_pre_qna( pre_qna ) :
    
    pre_qna = '\n\n'.join( [ '\n'.join( para.lines ) for para in pre_qna ] )
    
    m = speakers_re.search( pre_qna )
    
    if m :
        
        executives_text = m.group( 'executives' )
        analysts_text = m.group( 'analysts' )
        
        executives = [ p.group( 1 ).replace( '\r' , '' ).replace( '\n' , ' ' ).strip( ) for p in participants_re1.finditer( executives_text ) ]
        analysts = [ p.group( 1 ).replace( '\r' , '' ).replace( '\n' , ' ' ).strip( ) for p in participants_re1.finditer(analysts_text ) ]
        
        if not executives and not analysts :
            executives = [ p.group( ).replace( '\r' , '' ).replace( '\n' , ' ' ).strip( ) for p in participants_re2.finditer( executives_text ) ]
            analysts = [ p.group( ).replace( '\r' , '' ).replace( '\n' , ' ' ).strip( ) for p in participants_re2.finditer(analysts_text ) ]
            
        return 'Executives:\n' + '\n'.join( executives ) + '\n\nAnalysts:\n' + '\n'.join( analysts )



speaker_re1 = re.compile( r'^(?P<speaker>[A-Z][^a-z\s]+( &| [A-Z][^a-z\s]*)*):\s*(?P<speech>.*)$' )
speaker_re2 = re.compile( r'^([A-Z][^a-z\s]+( &| [A-Z][^a-z\s]*)*\s+-|OPERATOR$)' )

def prettify_qna( qna ) :
    
    mode = False
    
    i = 0
    while i < len( qna ) :
        m = speaker_re1.search( qna[ i ].lines[ 0 ] )
        if m :
            mode = True
            speaker = m.group( 'speaker' )
            speech = ' '.join( [ m.group( 'speech' ) ] + qna[ i ].lines[ 1 : ] )
            qna[ i ].lines = [ speaker , speech ] if speech else [ speaker ]
        elif mode and i > 0 :
            qna[ i - 1 ].lines.append( ' '.join( qna[ i ].lines ) )
            qna.pop( i )
            continue
        i += 1
    
    if mode : return qna
    
    i = 0
    while i < len( qna ) :
        m = speaker_re2.search( qna[ i ].lines[ 0 ] )
        if m :
            mode = True
            speaker = qna[ i ].lines[ 0 ]
            speech = ' '.join( qna[ i ].lines[ 1 : ] )
            qna[ i ].lines = [ speaker , speech ] if speech else [ speaker ]
        elif mode and i > 0 :
            qna[ i - 1 ].lines.append( ' '.join( qna[ i ].lines ) )
            qna.pop( i )
            continue
        i += 1
    
    return qna



if __name__ == '__main__' :
    
    if not os.path.isdir( intermediate_rep_out_dir ) :
        os.makedirs( intermediate_rep_out_dir )    
    
    if not os.path.isdir( out_dir ) :
        os.makedirs( out_dir )
    
    for file_name in os.listdir( data_dir ) :
        
        print file_name
        
        pages = pdf_to_pages( data_dir + '/' + file_name )        
        extract_headers( pages )
        extract_footers( pages )
        mend_split_paras( pages )
                
        out_file = open( intermediate_rep_out_dir + '/' + file_name[ : -4 ] + '.txt' , 'w' )        
        for page in pages :
            out_file.write( str( page ) )
        out_file.close( )
        
        paras = [ para for page in pages for para in page.paras ]
        pre_qna , qna , post_qna = extract_qna( paras )
        speakers = extract_speakers_from_pre_qna( pre_qna )
        qna = prettify_qna( qna )
        
        text = ( speakers + '\n\n' + '*' * 40 + '\n\n' if speakers else '' ) \
            + '\n\n'.join( [ '\n'.join( para.lines ) for para in qna ] ) + '\n'
        
        out_file = open( out_dir + '/' + file_name[ : -4 ] + '.txt' , 'w' )        
        out_file.write( text )
        out_file.close( )        
        