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


import re
import urllib2

from csv_utils import csv_write


cik_name_st_table_re = re.compile( r'<table class="tableFile2" summary="Results">(.*?)</table>' , re.I | re.S )

cik_name_st_tr_re = re.compile( r'<tr[^>]*>\s*'
                                + r'<td[^>]*><a[^>]*>(?P<cik>[^<]*)</a></td>\s*'
                                + r'<td[^>]*>(?P<name>[^<]*)</td>\s*'
                                + r'<td[^>]*>(<a[^>]*>(?P<st>[^<]*)</a>|\s*)</td>\s*'
                                + r'</tr>' )

items_re = re.compile( r'<span class="items">Items \d+ - (?P<last>\d+)</span>' )


def download_company_list( sic , save_path ) :
    
    first_item_index = 0
    items_per_page = 100
    
    rows = [ ]
    
    while True :
        
        url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=' + str( sic ) + '&owner=exclude&match=&start=' + str( first_item_index ) + '&count=' + str( items_per_page ) + '&hidefilings=0'
        print url
        response = urllib2.urlopen( url )
        html = response.read( )
        
        cik_name_st_table = cik_name_st_table_re.search( html ).group( )
        
        for m in cik_name_st_tr_re.finditer( cik_name_st_table ) :
            cik = int( m.group( 'cik' ) )
            name = m.group( 'name' ).replace( '&amp;' , '&' ).replace( '&#39;' , "'" )
            st = m.group( 'st' ) or ''            
            rows.append( [ sic , cik , name , st ] )
        
        if int( items_re.search( html ).group( 'last' ) ) != first_item_index + items_per_page : break
        first_item_index += items_per_page
    
    csv_write( save_path , headers = [ 'sic' , 'cik' , 'name' , 'st' ] , rows = rows )
    