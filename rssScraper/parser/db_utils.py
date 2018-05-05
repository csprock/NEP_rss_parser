import psycopg2
from psycopg2 import sql

import os

conn_info = {'dbname': os.environ['DB_NAME'],
             'username':os.environ['DB_USERNAME'],
             'password':os.environ['DB_PASSWORD'],
             'host':os.environ['DB_HOST']}

conn = connectToDatabase(conn_info)

base_query_1 = '''
        WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({}) 
        SELECT * FROM input_rows ON CONFLICT ({}) DO NOTHING RETURNING {}) 
        SELECT 'inserted' AS source, {} FROM ins UNION ALL 
        (SELECT 'selected' AS source, {}.{} FROM input_rows JOIN {} USING({}))
        '''

field_names = ['feed_id','content_id','date','headline']

table_name = sql.Identifier('articles')
fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))

id_name = sql.Identifier('article_id')
conflict_col = sql.Identifier('url')

# feed variables to psycopg2's sql statement formatter
q = sql.SQL(base_query_1).format(fields, placeholders, table_name, fields, conflict_col, id_name, id_name, table_name, id_name, table_name, conflict_col)

q.as_string(conn)



class databaseInserter:
    
    def __init__(self, conn_obj):
        
        self.conn = conn_obj
        
        self.article_query = '''
        WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({}) 
        SELECT * FROM input_rows ON CONFLICT ({}) DO NOTHING RETURNING {}) 
        SELECT 'inserted' AS source, {} FROM ins UNION ALL 
        (SELECT 'selected' AS source, {}.{} FROM input_rows JOIN {} USING({}))
        '''
        
        self.place_tag_query = '''
        WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({}) 
        SELECT * FROM input_rows ON CONFLICT ({}, {}) DO NOTHING RETURNING {}) 
        SELECT 'inserted' AS source, {} FROM ins UNION ALL 
        (SELECT 'selected' AS source, {}.{} FROM input_rows JOIN {} USING({}))
        '''
        
        self.place_mentions_query = '''
        INSERT INTO {}({}) VALUES ({})
        '''
        
        
        
        
        
        
        
        
        
        
        
        
        