import os
import sys

mypath = os.path.dirname(os.path.realpath('__file__'))
main_module = os.path.join(mypath, os.pardir + '/..')
sys.path.append(main_module)

from parsing_utils import make_place_filter, parse_feed, execute_insertions
from database_utils import connect_to_database, execute_query


conn_info = {'dbname': os.environ['DB_NAME'],
       # 'dbname':'test_database',
             'username':os.environ['DB_USERNAME'],
             'password':os.environ['DB_PASSWORD'],
             'host':os.environ['DB_HOST']}



conn = connect_to_database(conn_info)

# given media market, cycle through all publishers and feeds

market_id = 1
SG = make_place_filter(conn, market_id)
q = "SELECT feed_id, url FROM publishers INNER JOIN feeds ON publishers.pub_id = feeds.pub_id WHERE market_id = %s"

feeds = execute_query(conn, query = q, data = (market_id, ), return_values = True)

parsed_results = list()
for f in feeds:
    temp = parse_feed(f[1], f[0], SG)
    if temp is not None:
        parsed_results.extend(temp)
    
    
if parsed_results is not None:
    for r in parsed_results:
        execute_insertions(r, conn)
        
