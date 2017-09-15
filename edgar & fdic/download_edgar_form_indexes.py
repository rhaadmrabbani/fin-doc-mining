import urllib2
import re
import os.path

folder_re = re.compile( r'<a href="(?P<folder>\w+)/"><img [^>]*? alt="folder icon">' , re.I | re.S )

url = 'https://www.sec.gov/Archives/edgar/full-index/'
response = urllib2.urlopen( url )
html = response.read( )

junk_re = re.compile( r'^.*?(\r?\n *){3,}|(?<=\n)-+\r?\n' , re.S )

for m in folder_re.finditer( html ) :
    
    year = m.group( 'folder' )
    
    url = 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/'
    print url
    
    response = urllib2.urlopen( url )
    html = response.read( )
    
    for m in folder_re.finditer( html ) :

        qtr = m.group( 'folder' )
  
        url = 'https://www.sec.gov/Archives/edgar/full-index/' + year + '/' + qtr + '/master.idx'
        print url  
  
        save_path = 'edgar_form_indexes/' + year + '_' + qtr + '.idx'
        if not os.path.isfile( save_path ) :
            
            response = urllib2.urlopen( url )
            html = response.read( )
            
            html = junk_re.sub( '' , html )          
            
            save_file = open( save_path , 'w' )
            save_file.write( html )
            save_file.close( )
            