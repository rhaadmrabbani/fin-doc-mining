import os
import os.path
import re

from doc_fetcher_8k import fetch_docs
from para_mgr import get_paras
#from page_num_mgr import get_page_num_grps
#from hdr_mgr import get_hdr_grps , get_nth_hdr , get_rev_nth_hdr



inp_base_dir_path = '../forms/8-K'
out_base_dir_path = 'cleaned/8-K'
file_rel_paths = [ '{0}/{1}'.format( year , file_name ) for year in range( 2005 , 2017 )[ 0 :  ] for file_name in os.listdir( '{0}/{1}'.format( inp_base_dir_path , year ) )[  : ] ]
'''file_rel_paths = [ '2007/1378946_2007-04-13.txt' , '2008/1378946_2008-02-29.txt' , '2009/16614_2009-03-18.txt' , '2010/354869_2010-02-25.txt' , '2010/922487_2010-03-30.txt' , '2011/921557_2011-03-03.txt' , '2012/1108134_2012-03-15.txt' , 
                   '2012/921557_2012-03-07.txt' , '2013/1108134_2013-03-18.txt' , '2013/859222_2013-03-14.txt' , '2013/921557_2013-03-14.txt' , '2016/1228454_2016-03-14.txt' , '2016/1367859_2016-12-29.txt' ]'''
#file_rel_paths = [ '2014/1130144_2014-05-22.txt'  ]
    


hdr_re = re.compile(r'<sec-header>(?P<t>.*?)</sec-header>', re.I | re.S)
item_info_re = re.compile(r'item information:\s*(?P<t>.*?)\n', re.I)


file_rel_path_re = re.compile( '.*/(?P<cik>.*)_(?P<date>.*)' )

def main( ) :
    
    for file_rel_path in file_rel_paths :
        
        inp_file_path = '{0}/{1}'.format( inp_base_dir_path , file_rel_path )
        out_dir_path = '{0}/{1}'.format( out_base_dir_path , file_rel_path[ : -4 ] )
        #print inp_file_path , '->' , out_dir_path
        
        if not os.path.exists( out_base_dir_path ) :
            os.makedirs( out_base_dir_path )
            
        inp_file = open( inp_file_path , 'r' )
        text = inp_file.read( )
        inp_file.close( )
        
        hdr = hdr_re.search( text ).group( 't' )
        item_infos = [ 'ITEM INFORMATION: ' + info_match.group('t').strip() for info_match in item_info_re.finditer(hdr) ]
        output_text = '<SEC-HEADER>\n' + '\n'.join(item_infos) + '\n</SEC-HEADER>\n\n'        
        
        docs = fetch_docs( text )
        if not docs : continue
        paras = get_paras( docs[ 0 ] )
        #page_num_grps = get_page_num_grps( paras )
        #hdr_grps = get_hdr_grps( paras )
        docs[ 0 ].doc_text = '\n'.join( [ para.text for para in paras ] )

        if 1 : #file_rel_paths.index( file_rel_path ) % 20 == 0 or not hdr_grps :
            print inp_file_path , '->' , out_base_dir_path #, not hdr_grps
            print        
        
        m = file_rel_path_re.match( file_rel_path[ : -4 ] )
        out_path = '{0}/{1}-{2}.txt'.format( out_base_dir_path , m.group( 'date' ) , m.group( 'cik' ) )
        
        out_file = open( out_path , 'w' )
        out_file.write( output_text + docs[ 0 ].doc_text )
        out_file.close( )        


if __name__ == '__main__' :
    main( )