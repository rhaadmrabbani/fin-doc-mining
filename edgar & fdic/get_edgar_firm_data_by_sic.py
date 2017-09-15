sic_lo = 6000
sic_hi = 6999



import re
import urllib2



sic_table_re = re.compile( '<TABLE CELLSPACING=0 BORDER=0 CELLPADDING=4 WIDTH="100%">(?P<trs>.*?)</table>' , re.S )
sic_tr_re = re.compile( '<tr[^>]*>\s*<td[^>]*>(?P<sic>[^<]*)</td>' )


url = 'https://www.sec.gov/info/edgar/siccodes.htm'
print url    
response = urllib2.urlopen( url )
html = response.read( )

sic_table = sic_table_re.search( html ).group( 'trs' )
sics = [ int( m.group( 'sic' ) ) for m in sic_tr_re.finditer( sic_table ) ]
sics = [ sic for sic in sics if sic_lo <= sic <= sic_hi ]



items_re = re.compile( r'<span class="items">Items \d+ - (?P<last>\d+)</span>' )
cik_name_st_table_re = re.compile( r'<table class="tableFile2" summary="Results">(.*?)</table>' , re.I | re.S )
cik_name_st_tr_re = re.compile( r'<tr[^>]*>\s*<td[^>]*><a[^>]*>(?P<cik>[^<]*)</a></td>\s*<td[^>]*>(?P<name>[^<]*)</td>\s*<td[^>]*><a[^>]*>(?P<st>[^<]*)</a></td>\s*</tr>' )



cik_to_firm_data = { }

for sic in sics :
    
    start = 0
    count = 100
    
    while True :
        
        url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC={}&owner=exclude&match=&start={}&count={}&hidefilings=0'.format( sic , start , count )
        print url    
        response = urllib2.urlopen( url )
        html = response.read( )
        
        cik_name_st_table = cik_name_st_table_re.search( html ).group( )
        
        for m in cik_name_st_tr_re.finditer( cik_name_st_table ) :
            
            cik = int( m.group( 'cik' ) )
            name = m.group( 'name' ).replace( '&amp;' , '&' ).replace( '&#39;' , "'" )
            st = m.group( 'st' )
            
            cik_to_firm_data[ cik ] = ( name , sic , st )
        
        last = int( items_re.search( html ).group( 'last' ) )
        if last != start + count :
            break
        
        start += count
        
        
        
out = open( 'edgar_firm_data_by_sic.csv' , 'w' )
out.write( 'cik,name,sic,st\n' )

for cik in sorted( cik_to_firm_data ) : 
    name , sic , st = cik_to_firm_data[ cik ]
    out.write( '{},"{}",{},{}\n'.format( cik , name , sic , st ) )

out.close( )
