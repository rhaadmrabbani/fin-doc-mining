import re
import json
import getpass
import time
import mechanize
import os, os.path
    

months = [ 'JANUARY' , 'FEBRUARY' , 'MARCH' , 'APRIL' , 'MAY' , 'JUNE' , 'JULY' , 'AUGUST' , 'SEPTEMBER' , 'OCTOBER' , 'NOVEMBER' , 'DECEMBER' ]
delay_secs = 3800
batch_size = 900


def login( str_user , str_pass ) :
    
    print 'LOGGING IN'

    br = mechanize.Browser( )
    br.set_handle_robots( False )
    br.set_handle_refresh( False )
    
    resp = br.open( 'http://libproxy.rpi.edu/login?url=http://search.proquest.com/wallstreetjournal/advanced?accountid=28525' )
    print br
    
    br.select_form( nr = 0 )
    #br.form.set_all_readonly( False )
    br.form.new_control( 'text' , 'url' , { 'value' : 'http://search.proquest.com/wallstreetjournal/advanced?accountid=28525' } )
    br.form.new_control( 'text' , 'user' , { 'value' : str_user } )
    br.form.new_control( 'text' , 'pass' , { 'value' : str_pass } )
    br.form.new_control( 'text' , 'submit' , { 'value' : 'Login' } )

    resp = br.submit( )
    print br    

    return br


url_re = re.compile( r'http://search.proquest.com.libproxy.rpi.edu/wallstreetjournal/results/(?P<code>[^/]+)/1\?accountid=28525' )
count_re = re.compile( r'<h1 id="pqResultsCount">\s*(?P<count>[\d,]+) results\s</h1>' )
link_re = re.compile( r'<a id="citationDocTitleLink" [^>]* title="(?P<title>[^"]*)" [^>]* href="/wallstreetjournal/docview/(?P<code>[^/]+)/[^>]*>' )

def get_index( year , month , month_span , str_user , str_pass ) :    

    br = mechanize.Browser( )
    br.set_handle_robots( False )
    br.set_handle_refresh( False )
    
    resp = br.open( 'http://libproxy.rpi.edu/login?url=http://search.proquest.com/wallstreetjournal/advanced?accountid=28525' )
    print br
    
    br.select_form( nr = 0 )
    #br.form.set_all_readonly( False )
    br.form.new_control( 'text' , 'url' , { 'value' : 'http://search.proquest.com/wallstreetjournal/advanced?accountid=28525' } )
    br.form.new_control( 'text' , 'user' , { 'value' : str_user } )
    br.form.new_control( 'text' , 'pass' , { 'value' : str_pass } )
    br.form.new_control( 'text' , 'submit' , { 'value' : 'Login' } )

    resp = br.submit( )
    print br

    br.select_form( id = 'searchForm' )
    br[ 'queryTermField' ] = 'bank'
    br[ 'itemsPerPage' ] = [ '100' ]
    br[ 'select_multiDateRange' ] = [ 'RANGE' ]
    br[ 'month2' ] = [ months[ int( month ) - 1 ] ]
    br[ 'year2' ] = year
    br[ 'month2_0' ] = [ months[ int( month )  + month_span - 1 - 1 ] ]
    br[ 'year2_0' ] = year
    
    resp = br.submit( )
    print br
    
    url = resp.geturl( )
    html = resp.read( )
    
    code = url_re.match( url ).group( 'code' )
    
    count = int( count_re.search( html ).group( 'count' ).replace( ',' , '' ) )
    pages = count / 100 + 1
    
    out = open( 'wsj_index/' + year + '_' + month + '.txt' , 'a' )
        
    for i in range( 1 , pages + 1 ) :
        if i > 1 :
            resp = br.open( 'http://search.proquest.com.libproxy.rpi.edu/wallstreetjournal/results/' + code + '/' + str( i ) + '?accountid=28525' )
            html = resp.read( )
        link_ms = [ m for m in link_re.finditer( html ) ]
        for m in link_ms :
            out.write( json.dumps( [ m.group( 'code' ) , m.group( 'title' ) ] ) + '\n' )
        print str( i ) + ': ' + str( len( link_ms ) )
        if len( link_ms ) < 100 :
            break
    if i < pages - 2 :
        exit( 1 )


accesses = 0

def get_text_from_index( br , index , str_user , str_pass ) :

    global accesses

    out_dir = 'wsj_text/' + index
    if not os.path.isdir( out_dir ) :
        os.makedirs( out_dir )
    
    index_file = open( 'wsj_index/' + index + '.txt' )
    docs = index_file.readlines( )
    index_file.close( )
    
    docs = sorted( set( [ json.loads( d )[ 0 ] for d in docs ] ) )
    
    for doc in docs :
        
        out_path = 'wsj_text/' + index + '/' + doc + '.txt'
        
        if os.path.isfile( out_path ) :
            continue
        
        out = open( out_path , 'w' )

        resp = br.open( 'http://search.proquest.com.libproxy.rpi.edu/wallstreetjournal/docview/' + doc + '/' )
        accesses += 1
        print br
        
        text = resp.read( )

        if len( text ) < 100 :
            exit( 1 )
        
        out.write( text )
        
        link_m = re.compile( r'href="(/wallstreetjournal/docview/' + doc + r'/abstract/\w+/1\?accountid=28525)"' ).search( text )
        
        if not link_m :
            
            out.close( )

            br = login( str_user , str_pass )
            
            out = open( out_path , 'w' )

            resp = br.open( 'http://search.proquest.com.libproxy.rpi.edu/wallstreetjournal/docview/' + doc + '/' )
            accesses += 1
            print br
            
            text = resp.read( )
            out.write( text )
            
            link_m = re.compile( r'href="(/wallstreetjournal/docview/' + doc + r'/abstract/\w+/1\?accountid=28525)"' ).search( text )
        
        if not link_m and len( text ) < 100 :
            exit( 1 )
        
        if link_m :
            resp = br.open( 'http://search.proquest.com.libproxy.rpi.edu' + link_m.group( 1 ) )
            accesses += 1
            print br
            out.write( resp.read( ) )
        
        out.close( )
        
        if accesses >= batch_size :
            print 'SLEEPING'
            time.sleep( delay_secs )
            accesses = 0
            br = login( str_user , str_pass )


if __name__ == '__main__' :

    str_user = raw_input( 'Username: ' )
    str_pass = getpass.getpass( )       

    '''
    for year in [ '2009' , '2010' ] :
        
        month_span = 1 if year >= '2010' else 3                
 
        for month in [ str( month ).rjust( 2 , '0' ) for month in range( 1 , 13 , month_span ) ] :
            
            get_index( year , month , month_span , str_user , str_pass )
            time.sleep( 600 )
    '''
    br = login( str_user , str_pass )
    
    indexes = sorted( [ f[ : -4 ] for f in os.listdir( 'wsj_index' ) if f.endswith( '.txt' ) ] )
    indexes = indexes[ indexes.index( '2005_01' ) : ]
    
    for index in indexes :
        
        get_text_from_index( br , index , str_user , str_pass )
    
        
    