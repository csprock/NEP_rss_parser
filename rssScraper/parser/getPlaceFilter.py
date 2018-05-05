
import os, sys

if __name__ == '__main__':
    
    mypath = os.path.dirname(os.path.realpath('__file__'))
    sys.path.append(os.path.join(mypath, '...'))
    sys.path.append(os.path.join(mypath, os.pardir))

#from databaseTools import connectToDatabase
from entityFilter.makeGraphData import makeGraphData
from entityFilter.SearchGraph import SearchGraph


def getPlaceFilter(market_id, conn_obj):
    
        
    with conn_obj as con:
        with con.cursor() as curs:
            curs.execute("SELECT place_name, place_id FROM places WHERE market_id = %s", (market_id,))
            results = curs.fetchall()
            
            
    R, _, E = makeGraphData([n[0] for n in results])
    G = SearchGraph(R, results, E)
    return G
    



