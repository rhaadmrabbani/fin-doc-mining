# All classes used by this library are defined in this file.



class HtmlNode :
    
    def __init__( self , parent , tag , attrs ) :
        self.parent = parent
        self.depth = parent.depth + 1 if parent else 0
        self.tag = tag
        self.attrs = attrs
        self.children = [ ]



class Page :
    
    def __init__( self , text ) :        
        self.text = text
        self.headers = [ ]
        self.footers = [ ]
        self.header_page_num = ''
        self.footer_page_num = ''
        self.header_title = ''
        
    def __repr__( self ) :
        text = ''
        if self.headers :
            text += '[header]'
            if self.header_page_num : text += '[page {}]'.format( self.header_page_num )
            if self.header_title : text += str( [ self.header_title ] )
            text += '\n\n{0}\n\n{1}\n\n'.format( '\n\n'.join( [ header for header in self.headers ] ) , '=' * 40 )
        text += '{0}\n\n{1}\n\n'.format( self.text , '=' * 40 )
        if self.footers :
            text += '[footer]'
            if self.footer_page_num : text += '[page {}]'.format( self.footer_page_num )
            text += '\n\n{0}\n\n{1}\n\n'.format( '\n\n'.join( [ footer for footer in self.footers ] ) , '=' * 40 )
        return text
