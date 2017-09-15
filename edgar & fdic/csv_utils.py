import re



def parse_csv( path , headers = None , sep = ',' ) :

   csv_token_re = re.compile( r'(?P<nl>\r?\n)|(?P<sep>' + sep + r')|("(?P<quoted>[^"]*)"|(?P<unquoted>.*?))\s*?((?=' + sep + r')|(?=\r\n)|(?=\n)|(?=$))' , re.S )   
    
   inp = open( path )
   text = inp.read( )
   inp.close( )

   lines = [ [ ] ]
   prev_sep = False
   for m in csv_token_re.finditer( text ) :
      if m.group( 'nl' ) :
         lines.append( [ ] )
         prev_sep = False
      elif m.group( 'sep' ) :
         if prev_sep : lines[ -1 ].append( '' )
         prev_sep = True
      else :
         lines[ -1 ].append( m.group( 'quoted' ) or m.group( 'unquoted' ) or '' )
         prev_sep = False
   
   lines = lines[ : -1 ]
   
   if headers :   
      indices = [ lines[ 0 ].index( header ) for header in headers ]
      lines = [ [ line[ index ] for index in indices ] for line in lines ]
   
   return lines