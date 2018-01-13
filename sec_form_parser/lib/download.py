import os
import re
import sys


from utils.io_utils import *
from utils.utils import *



dir_re = re.compile( r'<a href="(?P<dir>\w+)/"><img [^>]*? alt="folder icon">' , re.I | re.S )

index_junk_re = re.compile( r'^.*?(\r?\n *){3,}|(?<=\n)-+\r?\n' , re.S )

nl_re = re.compile( r'\r?\n' )



# Function that downloads and saves (as csv files) all quarterly filing indexes available at SEC's online archive

def download_indexes( save_dir ) :

    listing_by_year = download( 'https://www.sec.gov/Archives/edgar/full-index/' )
    
    for m in dir_re.finditer( listing_by_year ) :
        
        year = m.group( 'dir' )        
        listing_by_qtr = download( 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/' )
        
        for m in dir_re.finditer( listing_by_qtr ) :
    
            qtr = m.group( 'dir' )            
            save_path = save_dir + '/' + year + '_' + qtr + '.csv'
            
            if os.path.isfile( save_path ) : continue
      
            idx = download( 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/' + qtr + '/master.idx' , debug = True )
            idx = index_junk_re.sub( '' , idx )
            rows = [ line.split( '|' ) for line in nl_re.split( idx ) if line ]
            
            save_csv( save_path , rows = rows )



# Function that combines downloaded indexes to one file, filtering by CIK and form-type if instructed

def combine_indexes( load_dir , save_path , filter_ciks = None , filter_form_types = None ) :
    
    if filter_ciks : filter_ciks = set( filter_ciks )
    if filter_form_types : filter_form_types = set( filter_form_types )
    
    all_rows = [ ]
    
    for i , filename in enumerate( sorted( os.listdir( load_dir ) ) ) :
        
        headers , rows = load_csv( load_dir + '/' + filename , debug = True )
        
        if i == 0 :
            cik_col = headers.index( 'CIK' )
            form_type_col = headers.index( 'Form Type' )
            
        all_rows += [ row for row in rows
                      if ( filter_ciks == None or int( row[ cik_col ] ) in filter_ciks )
                      and ( filter_form_types == None or row[ form_type_col ] in filter_form_types ) ]
        
    all_rows.sort( key = lambda row : int( row[ cik_col ] ) ) # group by CIK
    
    save_csv( save_path , headers = headers , rows = all_rows , debug = True )



div_re = re.compile( r'<tr[^>]*>\s*(<td[^>]*>[^<]*</td>\s*){2}<td[^>]*><a href="(?P<url>[^"]*\.(txt|html?))">\s*[^\s<]+\s*</a></td>\s*<td[^>]*>(?P<doc_type>10-K|EX-13[^<]*)</td>' )

doc_re = re.compile( r'<document>(?P<doc>.*?)</document>' , re.I | re.S )

doc_type_re = re.compile( r'<type>(?P<type>.*?)\n' , re.I )

doc_text_re = re.compile( r'<text>(?P<text>.*?)</text>' , re.I | re.S )

doc_pdf_re = re.compile( r'<pdf>.*?</pdf>' , re.I | re.S )



# Each 10-K form filing consists of several documents.
# SEC form filing index provides link to a giant text file that contains all documents for a given form filing instance.
# We only need to download relevant documents form each selected 10-K form (documents of type 10-K and EX-13x) and save. 

# Function that, given the link to the giant text file containing all documents, downloads only 10-K and EX-13x documents and returns a map from doc type to doc.

def download_10K_docs( url_from_index ) :
    
    doc_type_to_doc_map = { }

    raw_text = download( 'https://www.sec.gov/Archives/' + url_from_index[ : -4 ] + '-index.htm' )
    div_ms = list( div_re.finditer( raw_text ) )
    
    if div_ms :	
        for m in div_ms :
            url = 'https://www.sec.gov' + m.group( 'url' )
            if url.lower( ).endswith( '.pdf' ) : continue
	    doc = download( url , debug = True )
	    doc_type =  m.group( 'doc_type' )
	    doc_type_to_doc_map[ doc_type ] = doc
    else :		
        raw_text = download( 'https://www.sec.gov/Archives/' + url_from_index , debug = True )
        for doc_m in doc_re.finditer( raw_text ) :        
	    doc = doc_m.group( )
	    doc_type = doc_type_re.search( doc ).group( 'type' ).strip( )    
	    if doc_type != '10-K' and not doc_type.startswith( 'EX-13' ) or doc_pdf_re.search( doc ) : continue	    
	    doc_type_to_doc_map[ doc_type ] = doc
    
    return doc_type_to_doc_map



# Function that takes 10-K doc, EX-13x doc, or text in giant text file that contains all docs,
# strips away the metadata tags of each doc
# and returns a map from doc type to text in doc.

def extract_10K_docs( text ) :
    
    doc_type_to_text_map = { }    

    for doc_m in doc_re.finditer( text ) :
        
        doc = doc_m.group( )
        doc_type = doc_type_re.search( doc ).group( 'type' ).strip( )    
        if doc_type != '10-K' and not doc_type.startswith( 'EX-13' ) or doc_pdf_re.search( doc ) : continue
        doc_text = doc_text_re.search( doc ).group( 'text' )        
        doc_type_to_text_map[ doc_type ] = doc_text
    
    return doc_type_to_text_map
