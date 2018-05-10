import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), os.path.pardir))

from database_utils import connect_to_database, execute_query
from etl_utils import nytScraper, execute_insertions_nyt, generate_dates


CONN_INFO = {'dbname': os.environ['DB_NAME'],
             'username':os.environ['DB_USERNAME'],
             'password':os.environ['DB_PASSWORD'],
             'host':os.environ['DB_HOST']}
API_KEYS = os.environ['API_KEYS'].split(',')
TODAY, YESTERDAY = generate_dates()


conn = connect_to_database(CONN_INFO)

market_id = 1
q = "SELECT place_name, place_id FROM places WHERE market_id = %s"
place_list = execute_query(conn, q, data = (market_id, ), return_values = True)

apiScraper = nytScraper(API_KEYS)

results = list()
for p in place_list:
    p_name, p_id = p[0], p[1]
    time.sleep(1)
    print(p_name)
    r = apiScraper.run_query(page_range = 'all', q = '"' + p_name + '"', fq = {'glocations':'New York City'}, begin_date = YESTERDAY , end_date = TODAY)
    results.append( dict(place_id = p_id, query_results = r ) )
    
results = list(filter(lambda x: x['query_results'] != None, results))


counter = 0

import json
#with open('/home/carson/Documents/NIP/Data/test_downloads.json', 'w') as f:
#    json.dump(results, f)
#
with open('/home/carson/Documents/NIP/Data/test_downloads.json') as f:
    results = json.load(f)

feed_id = 4
for r_list in results:
    for r in r_list['query_results']:
        execute_insertions_nyt(conn, r, feed_id, r_list['place_id'])
        counter += 1
