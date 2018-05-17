import os
import sys

mypath = os.path.dirname(os.path.realpath('__file__'))
main_module = os.path.join(mypath, os.pardir + '/..')
sys.path.append(main_module)

from parsing_utils import make_place_filter, parse_feed, execute_insertions
from database_utils import connect_to_database, execute_query, CONN_INFO

conn = connect_to_database(CONN_INFO)

q1 = '''
    SELECT market_id FROM media_markets WHERE market_id IN (SELECT DISTINCT(places.market_id) FROM places)
    '''

markets = execute_query(conn, q1, data = None, return_values = True)

q2 = '''
    SELECT feed_id, url FROM publishers INNER JOIN feeds ON publishers.pub_id = feeds.pub_id 
    WHERE market_id = %s AND url IS NOT NULL
    '''

# given media market, cycle through all publishers and feeds
for m_id in markets:
    
    market_id = m_id[0]

    SG = make_place_filter(conn, market_id)
    
    feeds = execute_query(conn, query = q2, data = (market_id, ), return_values = True)
    
    parsed_results = list()
    for f in feeds:
        temp = parse_feed(f[1], f[0], SG)
        if temp is not None:
            parsed_results.extend(temp)
        
        
    if parsed_results is not None:
        for r in parsed_results:
            execute_insertions(r, conn)
        
conn.close()