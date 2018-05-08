import os
import sys
import time
import json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), os.path.pardir))

from database_utils import connect_to_database, execute_query
from etl_utils import nytScraper, execute_insertions_nyt


CONN_INFO = {'dbname': os.environ['DB_NAME'],
             'username':os.environ['DB_USERNAME'],
             'password':os.environ['DB_PASSWORD'],
             'host':os.environ['DB_HOST']}

API_KEYS = os.environ['API_KEYS'].split(',')


conn = connect_to_database(CONN_INFO)

market_id = 1
q = "SELECT place_name, place_id FROM places WHERE market_id = %s"
place_list = execute_query(conn, q, data = (market_id, ), return_values = True)


apiScraper = nytScraper(API_KEYS)

results = list()
for p in place_list[:3]:
    p_name, p_id = p[0], p[1]
    time.sleep(1)
    print(p_name)
    r = apiScraper.run_query(page_range = 'all', q = '"' + p_name + '"', fq = {'glocations':'New York City'}, begin_date = 20180301 , end_date = 20180331)
    results.append( dict(place_id = p_id, query_results = r ) )
    

results = list(filter(lambda x: x['query_results'] != None, results))

#with open('/home/carson/Documents/NIP/Data/march_downloads.json', 'w') as f:
#    json.dump(results, f)

#with open('C:/Users/csprock/Documents/Projects/Data Journalism/News Inequality Project/Data/march_downloads.json') as f:
#    data = json.load(f)

feed_id = 4
for r in results:
    execute_insertions_nyt(conn, r['query_results'], feed_id, r['place_id'])
