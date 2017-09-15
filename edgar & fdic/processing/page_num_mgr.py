import re



junk = r'(\s|<[^>]*>)*'
page_num_rs = '(F *- *)?\d+'



num_re = re.compile( r'\d+' )


class PageNum :
    
    def __init__( self , num , para_index ) :
        
        self.full_num = num
        self.actual_num = int( num_re.search( num ).group( ) ) if num else None
        self.num = self.actual_num
        self.para_index = para_index
        
    def __repr__( self ) :
        
        return ( '{1}' if not self.num or self.num == self.actual_num else '{0}({1})' ).format( self.num , self.full_num )



def get_page_num_grps( paras ) :
    
    page_nums = get_page_nums( paras )
    page_num_grps = group_page_nums( page_nums )
    
    return page_num_grps



page_sep_re = re.compile( r'^{0}?(<page>|table of contents){0}(?P<num>({1})?){0}$'.format( junk , page_num_rs ) , re.I | re.S )
page_sep_re2 = re.compile( r'^{0}(- *)?(?P<num>{1})( *-)?{0}$'.format( junk , page_num_rs ) , re.I | re.S )


def get_page_nums( paras ) :
        
    page_nums = [ ]
    
    for i in range( len ( paras ) ) :
        m = page_sep_re.match( paras[ i ].text )
        m2 = page_sep_re2.match( paras[ i ].text )
        if m :
            page_nums.append( PageNum ( m.group( 'num' ) , i ) )
        elif not paras[ i ].inside_table and m2 :
            page_nums.append( PageNum ( m2.group( 'num' ) , i ) )
    
    return page_nums



def group_page_nums( page_nums ) :
    
    if not page_nums : return [ ]
    
    page_num_grps = [ [ page_nums[ 0 ] ] ]
    
    for page_num in page_nums[ 1 : ] :
        if page_num.num and page_num.num > 200 :
            continue
        if ( page_num.num and page_num_grps[ -1 ][ -1 ].num and page_num_grps[ -1 ][ -1 ].num + 1 == page_num.num ) or ( not page_num.num and not page_num_grps[ -1 ][ -1 ].num ) :
            page_num_grps[ -1 ].append( page_num )
        else :
            page_num_grps.append( [ page_num ] )
                
    i = 1
    while i + 1 < len( page_num_grps ) :
        if page_num_grps[ i - 1 ][ -1 ].num and page_num_grps[ i + 1 ][ 0 ].num :
            if not page_num_grps[ i ][ 0 ].num and page_num_grps[ i - 1 ][ -1 ].num + 1 == page_num_grps[ i + 1 ][ 0 ].num :
                page_num_grps[ i - 1 : i + 2 ] = [ page_num_grps[ i - 1 ] + page_num_grps[ i + 1 ] ]
                continue
            elif page_num_grps[ i - 1 ][ -1 ].num + len( page_num_grps[ i ] ) + 1 == page_num_grps[ i + 1 ][ 0 ].num :
                for j in range( len( page_num_grps[ i ] ) ) :
                    page_num_grps[ i ][ j ].num = page_num_grps[ i - 1 ][ -1 ].num + 1 + j
                page_num_grps[ i - 1 : i + 2 ] = [ page_num_grps[ i - 1 ] + page_num_grps[ i ] + page_num_grps[ i + 1 ] ]
                continue
        i += 1
        
    page_num_grps = [ page_num_grp for page_num_grp in page_num_grps if len( page_num_grp ) > 1 ]
    
    return page_num_grps
