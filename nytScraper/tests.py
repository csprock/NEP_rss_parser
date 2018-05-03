


####### testing of the API scraper ###########

from queryAPI import nytScraper
from etl_config import API_KEYS
import json

apiScraper = nytScraper(API_KEYS)

results = apiScraper.runQuery('all', q = 'Harlem', fq = {'glocations':'New York City'}, begin_date = 20180301 , end_date = 20180331)

# save results 
with open('C:/Users/csprock/Documents/Projects/Data Journalism/News Inequality Project/Data/Downloads/harlem_march_18.json', 'w') as f:
    json.dump(results, f)



########### testing queries ##############
    
from etl_config import CONN_INFO
from etl_utils import databaseInserter
from psycopg2 import sql
import psycopg2

import time

# open Harlem test files
with open('C:/Users/csprock/Documents/Projects/Data Journalism/News Inequality Project/Data/Downloads/harlem.json') as f:
    results = json.load(f)




db_inserter = databaseInserter(CONN_INFO)



for r in results:
    db_inserter.executeInsertion(feed_id = 5, place_id = 599, data = r)
    time.sleep(0.5)









val = makeArticleTuple(5, results[11], as_dict = True)   


# harlem id = 599
# feed id = 5


test_inserter = databaseInserter(CONN_INFO)

test_inserter.executeInsertion(feed_id = 5, place_id = 599, data = results[11])



conn = connectToDatabase(CONN_INFO)



# article insert query



base_query = '''
            WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({}) 
            SELECT * FROM input_rows ON CONFLICT (url) DO NOTHING RETURNING id) 
            SELECT 'inserted' AS source, id FROM ins UNION ALL 
            (SELECT 'selected' AS source, {}.id FROM input_rows JOIN {} USING(url))
            '''


##### dynamically generate insertion statements based on null values #####
 
def generateSQL_1(values):
    
    f_dict = {k:v for k, v in values.items() if v != None}
    
    field_names = f_dict.keys()
    
    # create SQL variables
    table_name = sql.Identifier('articles')
    fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
    placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))
    
    # feed variables to psycopg2's sql statement formatter
    q = sql.SQL(base_query).format(fields, placeholders, table_name, fields, table_name, table_name)
    return q


q2 = generateSQL_1(val)

with conn:
    with conn.cursor() as curs:
        curs.execute(q2, val)
        res = curs.fetchall()
        
        
        
        
base_query_2 = "INSERT INTO {}({}) VALUES ({})"

val2 = makePlaceMentionsTuple(article_id = res[0][1],place_id = 599, as_dict = True)

def generateSQL_2(values):
    
    field_names = values.keys()
    
    table_name = sql.Identifier('place_mentions')
    fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
    placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))
    
    q = sql.SQL(base_query_2).format(table_name, fields, placeholders)
    return q



q2 = generatePlaceMentions(val2)

with conn:
    with conn.cursor() as curs:
        curs.execute(q2, val2)






    
    
    
    
    
    
    
valueTuple1 = makeArticleTuple(5, results[11], as_dict = True)
q1 = generateSQL_1(valueTuple1)

with conn as con:
    with con.cursor() as curs:
        curs.execute(q1, valueTuple1)
        returned_id = curs.fetchall()
        

valueTuple2 = makePlaceMentionsTuple(returned_id[0][1], 599, as_dict = True)
q2 = generateSQL_2(valueTuple2)

with conn as con:
    with con.cursor() as curs:
        curs.execute(q2, valueTuple2)
    
    
    
    
    
    
    

