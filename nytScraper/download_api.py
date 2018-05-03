


from queryAPI import nytScraper

from etl_config import CONN_INFO, API_KEYS
import pandas as pd
import json
import time

q = "SELECT id, place_name, geocode FROM places WHERE market_id = 2"

places = executeSQL_select(q, None, CONN_INFO)

apiScraper = nytScraper(API_KEYS)

#db_inserter = databaseInserter(CONN_INFO)

results = list()

for p in places.iterrows():
    p_id = p[1][0]
    p_name = p[1][1]
    time.sleep(1)
    print(p_name)
    r = apiScraper.runQuery('all', q = '"' + p_name + '"', fq = {'glocations':'New York City'}, begin_date = 20180301 , end_date = 20180331)
    results.append( dict(place_id = p_id, query_results = r ) )
    

with open('C:/Users/csprock/Documents/Projects/Data Journalism/News Inequality Project/Data/march_downloads.json', 'w') as f:
    json.dump(results, f)



from etl_config import CONN_INFO
from etl_utils import databaseInserter

with open('C:/Users/csprock/Documents/Projects/Data Journalism/News Inequality Project/Data/march_downloads.json') as f:
    data = json.load(f)
    


data = list(filter(lambda x: x['query_results'] != None, data))



db_inserter = databaseInserter(CONN_INFO)   
    
    
for d in data:
    time.sleep(0.1)
    
    
    c = 0
    for r in d['query_results']:
        time.sleep(0.1)
        db_inserter.executeInsertion(5, d['place_id'], r)
        c += 1
    print("Finished writing %s entries from place_id %s" % (str(c), d['place_id']))
        
        
    