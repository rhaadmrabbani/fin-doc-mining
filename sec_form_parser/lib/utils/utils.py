# utils.py
# Author: Rhaad M. Rabbani (2017)

# This file contains general utility functions intended for use by the user.



############################################################
## General utility functions intended for use by the user ##
############################################################



# Utility function that groups items based on adjacency_check

def group_items( items , adjacency_check ) :
    
    groups = [ ]
    if items :
        groups.append( [ items[ 0 ] ] )
        for item in items[ 1 : ] :
            if adjacency_check( groups[ -1 ][ -1 ] , item ) : groups[ -1 ].append( item )
            else : groups.append( [ item ] )
            
    return groups

