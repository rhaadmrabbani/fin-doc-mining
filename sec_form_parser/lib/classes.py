# classes.py
# Author(s): Rhaad M. Rabbani (2017)

# All classes used by this library are defined in this file.



from utils.utils import *
from utils.text_utils import *



class HtmlNode :
    
    def __init__( self , parent , tag , attrs ) :
        self.parent = parent
        self.depth = parent.depth + 1 if parent else 0
        self.tag = tag
        self.attrs = attrs
        self.children = [ ]



class TextSegment :
    
    def __init__( self , text ) :
        self.text = text
        self.tag_masked_text = tag_re.sub( '' , text )
        self.is_page_break = False
        self.is_footer = False
        self.is_header = False
        self.page_num = ''



class Page :
    
    def __init__( self ) :
        self.text = ''
        self.text_segments = [ ]
        self.header = [ ]
        self.header_page_num = ''
        self.footer = [ ]
        self.footer_page_num = ''
        
    def __repr__( self ) :
        text = ''
        if self.header :
            text += '[header]'
            if self.header_page_num : text += '[page {}]'.format( self.header_page_num )
            text += '\n{0}\n\n{1}\n\n'.format( '\n'.join( [ segment.text for segment in self.header ] ) , '=' * 40 )        
        text += '{0}\n\n{1}\n\n'.format( self.text , '=' * 40 )
        if self.footer :
            text += '[footer]'
            if self.footer_page_num : text += '[page {}]'.format( self.footer_page_num )
            text += '\n{0}\n\n{1}\n\n'.format( '\n'.join( [ segment.text for segment in self.footer ] ) , '=' * 40 )
        return text
        
        

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
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,  OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
