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


import urllib2
import re
import os.path


form_10K_div_re = re.compile( r'<tr>\s*(<td[^>]*>[^<]*</td>\s*){2}<td[^>]*><a href="(?P<link>[^"]*)">(?P<filename>[^<]*)</a></td>\s*<td[^>]*>10-K</td>' )


def download_10K( link , save_path ) :
    
    if os.path.isfile( save_path ) : return
    
    url = 'https://www.sec.gov/Archives/' + link[ : -4 ] + '-index.htm'
    response = urllib2.urlopen( url , timeout = 10 )
    html = response.read( )
    
    m = form_10K_div_re.search( html )
    url = 'https://www.sec.gov' + m.group( 'link' ) if m and m.group( 'filename' ) else 'https://www.sec.gov/Archives/' + link
    print url ,        
    response = urllib2.urlopen( url , timeout = 10 )
    html = response.read( )
    
    save_dir = os.path.dirname( save_path )    
    if save_dir and not os.path.isdir( save_dir ) : os.makedirs( save_dir )    
    
    print 'Saving to ' + save_path
    save_file = open( save_path , 'w' )
    save_file.write( html )
    save_file.close( )