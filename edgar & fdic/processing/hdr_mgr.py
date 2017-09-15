import re



junk = r'(\s|<[^>]*>)*'



item_num_err_re = re.compile( r'[il]' , re.I )
junk_re = re.compile( junk )
num_re = re.compile( r'\d+' )
hdr_tag_re = re.compile( r'<.*?>' , re.I )


class Hdr :
    
    def __init__( self , num , para_index , paras ) :
        
        self.full_num = junk_re.sub( '' , item_num_err_re.sub( '1' , num ) ) if num else None
        self.num = int( num_re.search( self.full_num ).group( ) ) if num else None
        self.para_index = para_index
        self.tagged = hdr_tag_re.search( paras[ para_index ].text ) != None
        self.inside_table = paras[ para_index ].inside_table
        
    def __repr__( self ) :
        
        return '{0}:{1}'.format( self.full_num , self.inside_table )


item_re = re.compile( 'i ?t ?e ? m' , re.I )


def get_hdr_grps( paras ) :
    
    hdrs = get_hdrs( paras )
    hdr_grps = group_hdrs( hdrs )
    
    if not hdr_grps : return hdr_grps
        
        
    good_hdr_para_is = [ hdr.para_index for hdr_grp in hdr_grps for hdr in hdr_grp ]
    all_hdr_para_is = [ i for i in range( len ( paras ) ) if hdr_re.match( paras[ i ].text ) ]
    bad_hdr_para_is = set( all_hdr_para_is ) - set( good_hdr_para_is )
    
    for para_i in bad_hdr_para_is :
        paras[ para_i ].text = item_re.sub( '' , paras[ para_i ].text )
    
    return hdr_grps



hdr_re = re.compile( r'^{0}((part{0}(\S+?{0}){{1,2}})?i{0}t{0}e{0}ms?\.?{0}(?P<num>[\dil]+({0}|[^<>])*)((?=[a-z][a-z])|\n$)|part |signature)'.format( junk ) , re.I | re.S )
maybe_bad_hdr_re = re.compile( r'part(.*)item' , re.I )
bad_item_num_re = re.compile( r'\.[il\d]|,' )
bad_item_para_re = re.compile( r'^{0}items?{0}[a-z]{{2}}'.format( junk ) , re.I )


def get_hdrs( paras ) :
    
    hdrs = [ ]
    
    for i in range( len ( paras ) ) :
        m = hdr_re.match( paras[ i ].text )
        if m :
            if ( m.group( 'num' ) and bad_item_num_re.search( m.group( 'num' ) ) ) \
               or bad_item_para_re.match( paras[ i ].text ) :
                continue
            m2 = maybe_bad_hdr_re.search( paras[ i ].text )
            if m2 and ',' in m2.group( 1 ) :
                continue
            hdrs.append( Hdr ( m.group( 'num' ) , i , paras ) )
    
    return hdrs



def group_hdrs( hdrs ) :
    
    prev = get_nth_hdr( hdrs , 1 )
    if not prev : return [ ]
    
    hdr_grps = [ [ prev ] ]    
    for hdr in hdrs[ hdrs.index( prev ) + 1 : ] :
        if hdr.num and hdr.num >= 20 :
            continue
        if not hdr.num or prev.num <= hdr.num <= prev.num + 1 and hdr.inside_table == prev.inside_table :
            hdr_grps[ -1 ].append( hdr )
        else :
            hdr_grps.append( [ hdr ] )
        if hdr.num : prev = hdr   
    
    if len( [ hdr_grp for hdr_grp in hdr_grps if not ( hdr_grp[ 0 ].num == 1 and 14 <= get_rev_nth_hdr( hdr_grp , 1 ).num <= 16 ) ] ) <= 1 :
        return hdr_grps        
    
    ####
    
    new_hdr_grps = [ hdr_grps[ 0 ][ : ] ]
    for hdr_grp in hdr_grps[ 1 : ] :
        prev = get_rev_nth_hdr( new_hdr_grps[ -1 ] , 1 )
        if prev.num <= hdr_grp[ 0 ].num <= prev.num + 1 or ( prev.num <= hdr_grp[ 0 ].num and hdr_grp[ 0 ].inside_table == prev.inside_table ) :
            new_hdr_grps[ -1 ] += hdr_grp
        else :
            new_hdr_grps.append( hdr_grp[ : ] )
    
    if len( [ hdr_grp for hdr_grp in new_hdr_grps if not ( hdr_grp[ 0 ].num == 1 and 14 <= get_rev_nth_hdr( hdr_grp , 1 ).num <= 16 ) ] ) <= 1 :
        return new_hdr_grps    
    
    ####
    
    good_hdr_grps = [ ]
    for hdr_grp in hdr_grps :
        if hdr_grp[ 0 ].num == 1 and 14 <= get_rev_nth_hdr( hdr_grp , 1 ).num <= 16 :
            hdr_grps.remove( hdr_grp )
            good_hdr_grps.append( hdr_grp )
        else :
            break
    
    new_hdr_grps = [ hdr_grp for hdr_grp in hdr_grps if not hdr_grp[ 0 ].inside_table ]
    #print hdr_grps
    if not new_hdr_grps : return None
    
    new_hdr_grps2 = [ new_hdr_grps[ 0 ][ : ] ]
    for hdr_grp in new_hdr_grps[ 1 : ] :
        prev = get_rev_nth_hdr( new_hdr_grps2[ -1 ] , 1 )
        if prev.num <= hdr_grp[ 0 ].num <= prev.num + 1 or ( prev.num <= hdr_grp[ 0 ].num and hdr_grp[ 0 ].inside_table == prev.inside_table ) :
            new_hdr_grps2[ -1 ] += hdr_grp
        else :
            new_hdr_grps2.append( hdr_grp[ : ] )    
    
    new_hdr_grps2 = good_hdr_grps + new_hdr_grps2
    
    if len( [ hdr_grp for hdr_grp in new_hdr_grps2 if not ( hdr_grp[ 0 ].num == 1 and 14 <= get_rev_nth_hdr( hdr_grp , 1 ).num <= 16 ) ] ) <= 1 :
        return new_hdr_grps
    
    ####   
    print hdr_grps
    return None



def get_nth_hdr( hdrs , n ) :

    for hdr in hdrs :
        if hdr.num :
            n -= 1
            if n == 0 :
                return hdr
            


def get_rev_nth_hdr( hdrs , n ) :

    for hdr in hdrs[ : : -1 ] :
        if hdr.num :
            n -= 1
            if n == 0 :
                return hdr
