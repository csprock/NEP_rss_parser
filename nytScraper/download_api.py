import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), os.path.pardir))

from database_utils import connect_to_database, execute_query, CONN_INFO
from etl_utils import nytScraper, execute_insertions_nyt, generate_dates, execute_api_search

# define session constants
API_KEYS = os.environ['API_KEYS'].split(',')
TODAY, YESTERDAY = generate_dates()
MARKET_ID = 1
FEED_ID = 4
RERUN_PATH = '/home/carson/Documents/NIP/NewsInequalityProjectETL/reruns.json'

apiScraper = nytScraper(API_KEYS)

# execute any reruns from last session
with open(RERUN_PATH, 'r') as f:
    to_rerun = json.load(f)

results, reruns = list(), list()
if len(to_rerun) > 0:

    for data in to_rerun:

        today = data['date']['today']
        yesterday = data['date']['yesterday']

        old_results, old_reruns = execute_api_search(scraper = apiScraper, place_list = data['place_list'], market_id = MARKET_ID, today = today, yesterday = yesterday)
        results.extend(old_results)
        reruns.extend(old_reruns)


conn = connect_to_database(CONN_INFO)

q = "SELECT place_name, place_id FROM places WHERE market_id = %s"
place_list = execute_query(conn, q, data = (MARKET_ID, ), return_values = True)

new_results, new_reruns = execute_api_search(scraper = apiScraper, place_list = place_list, market_id = MARKET_ID, today = TODAY, yesterday = YESTERDAY)

results.extend(new_results)

try:
    reruns.append(new_reruns)
    reruns = [r for r in reruns if r != None]   # bugfix for returned None
except TypeError:
    pass

# serialize reruns
with open(RERUN_PATH, 'w') as f:
    json.dump(reruns, f)



for r_list in results:
    for r in r_list['query_results']:
        execute_insertions_nyt(conn, r, FEED_ID, r_list['place_id'])

conn.close()
