import os
import psycopg2
from psycopg2 import sql

CONN_INFO = {'dbname': os.environ['DB_NAME'],
             'username':os.environ['DB_USERNAME'],
             'password':os.environ['DB_PASSWORD'],
             'host':os.environ['DB_HOST']}

def connect_to_database(conn_info, success_message = True):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (conn_info['host'], conn_info['dbname'], conn_info['username'], conn_info['password'])
    try:
        conn = psycopg2.connect(conn_string)
        if success_message is True:
            print("Connected to database %s." % (conn_info['dbname']))

        return conn
    except:
        print('Error! Failure to connect to database %s' % (conn_info['dbname']))


def execute_query(conn_obj, query, data = None, return_values = False):

    with conn_obj as conn:
        with conn.cursor() as curs:
            if data is not None:
                curs.execute(query, data)
                if return_values:
                    to_return = curs.fetchall()
            else:
                curs.execute(query)
                if return_values:
                    to_return = curs.fetchall()

    if return_values:
        return to_return



def generate_article_query(field_names):

    article_query = '''
    WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({})
    SELECT * FROM input_rows ON CONFLICT ({}) DO NOTHING RETURNING {})
    SELECT 'inserted' AS source, {} FROM ins UNION ALL
    (SELECT 'selected' AS source, {}.{} FROM input_rows JOIN {} USING({}))
    '''

    table_name = sql.Identifier('articles')
    id_name = sql.Identifier('article_id')
    conflict_col = sql.Identifier('url')

    fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
    placeholders = sql.SQL(', ').join(map(sql.Placeholder, field_names))

    q_string = sql.SQL(article_query).format(fields, placeholders, table_name, fields,
                      conflict_col, id_name,
                      id_name,
                      table_name, id_name, table_name, conflict_col)

    return q_string


def generate_tag_query(field_names):

    place_tag_query = '''
    WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({})
    SELECT * FROM input_rows ON CONFLICT ({}, {}) DO NOTHING RETURNING {})
    SELECT 'inserted' AS source, {} FROM ins UNION ALL
    (SELECT 'selected' AS source, {}.{} FROM input_rows JOIN {} USING({},{}))
    '''


    table_name = sql.Identifier('place_tags')
    id_name = sql.Identifier('tag_id')
    conflict_col_1 = sql.Identifier('article_id')
    conflict_col_2 = sql.Identifier('place_id')

    fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
    placeholders = sql.SQL(', ').join(map(sql.Placeholder, field_names))

    q_string = sql.SQL(place_tag_query).format(fields, placeholders, table_name, fields,
                      conflict_col_1, conflict_col_2, id_name,
                      id_name,
                      table_name, id_name, table_name, conflict_col_1, conflict_col_2)

    return q_string

def generate_place_mentions_query(field_names):

    place_mentions_query = '''
    INSERT INTO {}({}) VALUES ({})
    '''

    table_name = sql.Identifier('place_mentions')

    fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
    placeholders = sql.SQL(', ').join(map(sql.Placeholder, field_names))

    q_string = sql.SQL(place_mentions_query).format(table_name, fields, placeholders)
    return q_string


def generate_keyword_query(field_names):

    keyword_query = '''
    INSERT INTO {}({}) VALUES ({}) ON CONFLICT DO NOTHING
    '''

    table_name = sql.Identifier('keywords')

    fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
    placeholders = sql.SQL(', ').join(map(sql.Placeholder, field_names))

    q_string = sql.SQL(keyword_query).format(table_name, fields, placeholders)
    return q_string
