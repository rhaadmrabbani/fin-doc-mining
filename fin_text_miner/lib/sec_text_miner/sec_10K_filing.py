import re
import sys


sys.path.append('../lib')
from utils import load_text , save_text , load_csv , save_csv, download


div_re = re.compile( r'<tr[^>]*>\s*(<td[^>]*>[^<]*</td>\s*){2}<td[^>]*><a href="(?P<url_from_filing_index>[^"]*\.txt)">\s*[^\s<]+\s*</a></td>\s*<td[^>]*>(?P<doc_type>10-K|EX-13[^<]*)</td>' )

doc_re = re.compile( r'<document>(?P<doc>.*?)</document>' , re.I | re.S )

doc_type_re = re.compile( r'<type>(?P<type>.*?)\n' , re.I )

doc_text_re = re.compile( r'<text>(?P<text>.*?)</text>' , re.I | re.S )

doc_pdf_re = re.compile( r'<pdf>.*?</pdf>' , re.I | re.S )


# download 10-K and EX-13x docs, given relative url of txt file containing all 10-K related docs,
# and return dictionary containing map from document type to text

def download_10K_docs( url_from_filing_index ) :
    

    
    raw_text = download( 'https://www.sec.gov/Archives/' + url_from_filing_index[ : -4 ] + '-index.htm' )
    div_ms = list( div_re.finditer( raw_text ) )
    
    if div_ms :
	
	docs = { }
        for m in div_ms :
            url = 'https://www.sec.gov' + m.group( 'url_from_filing_index' )
            if url.lower( ).endswith( '.pdf' ) : continue
            doc = download( url , debug = True )
            doc_type = m.group( 'doc_type' )
            doc_text = doc_text_re.search( doc ).group( 'text' )
            docs[ doc_type ] = doc_text
			
    else :
		
        raw_text = download( 'https://www.sec.gov/Archives/' + url_from_filing_index , debug = True )
        docs = extract_10K_docs( raw_text )
    
    return docs


def extract_10K_docs( raw_text ) :
    
    docs = { }    

    for doc_m in doc_re.finditer( raw_text ) :
        
        doc = doc_m.group( 'doc' )
        doc_type = doc_type_re.search( doc ).group( 'type' ).strip( )    
        if not ( doc_type == '10-K' or doc_type.startswith( 'EX-13' ) ) : continue
        doc_text = doc_text_re.search( doc ).group( 'text' )
        if doc_pdf_re.search( doc_text ) : continue
        
        docs[ doc_type ] = doc_text
    
    return docs

