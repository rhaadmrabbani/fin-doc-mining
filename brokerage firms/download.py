import urllib2
import re
import os
import os.path
from collections import defaultdict


sic_to_ciks = defaultdict( list )

items_re = re.compile( r'<span class="items">Items \d+ - (?P<last>\d+)</span>' )
cik_name_st_table_re = re.compile( r'<table class="tableFile2" summary="Results">(.*?)</table>' , re.I | re.S )
cik_name_st_tr_re = re.compile( r'<tr[^>]*>\s*<td[^>]*><a[^>]*>(?P<cik>[^<]*)</a></td>\s*<td[^>]*>(?P<name>[^<]*)</td>\s*<td[^>]*><a[^>]*>(?P<st>[^<]*)</a></td>\s*</tr>' )

for sic in [ '6200' , '6211' , '6221' , '6282' ] :
    
    start = 0
    count = 100
    
    while True :
        
        url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=' + sic + '&owner=exclude&match=&start=' + str( start ) + '&count=' + str( count ) + '&hidefilings=0'
        print url    
        response = urllib2.urlopen( url )
        html = response.read( )
        
        cik_name_st_table = cik_name_st_table_re.search( html ).group( )
        
        for m in cik_name_st_tr_re.finditer( cik_name_st_table ) :
            
            cik = m.group( 'cik' )
            name = m.group( 'name' )
            st = m.group( 'st' )
            
            sic_to_ciks[ sic ].append( cik )
        
        last = int( items_re.search( html ).group( 'last' ) )
        if last != start + count :
            break
        
        start += count


'''
cik_sic_table_re = re.compile( r'<table[^>]*\sid="cos"[^>]*>(.*?)</table>' , re.I | re.S )
cik_sic_tr_re = re.compile( r'<tr[^>]*>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*>(?P<cik>[^<]*)</td>\s*<td[^>]*>(?P<sic>[^<]*)</td>\s*</tr>' , re.I | re.S )


for c in ( [ chr( ord( 'a' ) + i ) for i in range( 20 ) ] + [ 'uv' , 'wxyz' ] ) :

    url = 'https://www.sec.gov/divisions/corpfin/organization/cfia-{}.htm'.format( c )
    print url
    
    response = urllib2.urlopen( url )
    html = response.read( )    

    cik_sic_table = cik_sic_table_re.search( html ).group( )
    
    for m in cik_sic_tr_re.finditer( cik_sic_table ) :
        
        cik = m.group( 'cik' )
        sic = m.group( 'sic' )
        
        if sic in [ '6200' , '6211' , '6221' , '6282' ] :
            
            sic_to_ciks[ sic ].append( cik )
'''


for year in range( 2006 , 2017 ) :
    
    for sic , ciks in sic_to_ciks.iteritems( ) :
        path = 'forms/' + sic
        if not os.path.exists( path ) :
            os.makedirs( path )
    
    for qtr in range( 1 , 5 ) :
        
        index_path = '../data/form_index/' + str( year ) + '_QTR' + str( qtr ) + '.idx'
        index_file = open( index_path )
        index = index_file.readlines( )
        index_file.close( )
        
        for i in range( len( index ) ) :
            if index[ i ].startswith( '--' ) :
                index = index[ i + 1 : ]
                break
        
        for line in index :
            
            cik , company , form_type , date , link = line.strip( ).split( '|' )
            
            if form_type != '10-K' :
                continue
            
            for sic , ciks in sic_to_ciks.iteritems( ) :     
            
                if cik in ciks :
                    
                    url = 'https://www.sec.gov/Archives/' + link
                    print url
                    
                    save_path = 'forms/' + sic + '/' + cik + '_' + date + '.txt'
                    print save_path
                    print
                    
                    if not os.path.isfile( save_path ) :
                        
                        response = urllib2.urlopen( url )
                        html = response.read( )
                        
                        save_file = open( save_path , 'w' )
                        save_file.write( html )
                        save_file.close( )


