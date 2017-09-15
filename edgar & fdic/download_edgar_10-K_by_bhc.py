import urllib2
import re
import os , os.path
import datetime
from collections import defaultdict
import csv_utils



form_div_re = re.compile( r'<tr>\s*(<td[^>]*>[^<]*</td>\s*){2}<td[^>]*><a href="(?P<link>[^"]*)">[^<]*</a></td>\s*<td[^>]*>10-K</td>' )

def download_10K( link ) :
    
    url = 'https://www.sec.gov/Archives/' + link[ : -4 ] + '-index.htm'
    response = urllib2.urlopen( url , timeout = 10 )
    html = response.read( )
    
    m = form_div_re.search( html )
    if not m : return None
    
    url = 'https://www.sec.gov' + m.group( 'link' )
    response = urllib2.urlopen( url , timeout = 10 )
    html = response.read( )
    
    return html



def save_to_file( save_path , text ) :
    
    save_file = open( save_path , 'w' )
    save_file.write( text )
    save_file.close( )    



out_dir = 'edgar_forms/10-K'
if not os.path.exists( out_dir ) :
    os.makedirs( out_dir )



index = csv_utils.parse_csv( 'edgar_10-K_index_by_sic.idx' , sep = r'\|' )

cik_to_lines = defaultdict( list )

for line in index[ 1 : ] :
    cik , name , form_type , date , link = line
    cik_to_lines[ int( cik ) ].append( line )
    
ciks = sorted( cik_to_lines )



bhc_re = re.compile( r'bank\s*holding\s*company' , re.I )



count = 0
bhc_count = 0

print len( ciks )

for cik in ciks :
    
    done = True
    for _ , name , form_type , date , link in cik_to_lines[ cik ] :
        if not os.path.isfile( '{}/{}-{}.txt'.format( out_dir , date , cik ) ) : done = False
    if done : continue
    
    for i in range( -1 , - len( cik_to_lines[ cik ] ) - 1 , -1 ) :
        _ , name , form_type , date , link = cik_to_lines[ cik ][ i ]    
        html = download_10K( link )
        if html :
            break
    
    if html and bhc_re.search( html ) :
        
        bhc_count += 1
        #save_to_file( '{}/{}-{}.txt'.format( out_dir , date , cik ) , html )
        
        for _ , name , form_type , date , link in cik_to_lines[ cik ] :
            html = download_10K( link )
            if not html : continue
            save_to_file( '{}/{}-{}.txt'.format( out_dir , date , cik ) , html )
            
    else :
        for _ , name , form_type , date , link in cik_to_lines[ cik ] :
            save_to_file( '{}/{}-{}.txt'.format( out_dir , date , cik ) , '' )        
        
    count += 1
    
    if count % 5 == 0 :
        now = datetime.datetime.now()
        print bhc_count , '/' , count , ':' ,  now.hour , now.minute , now.second    
