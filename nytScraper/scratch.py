from psycopg2 import sql
import psycopg2

conn = connectToDatabase(CONN_INFO)

values = [('Chris', 'chris@gmail.com','IBM'), ('Krystal','krystal@email.com',None)]




comp = sql.Identifier(values[1][0]) + sql.Identifier(values[1][1]) + sql.Literal(None)
comp.join(', ').as_string(conn)

colnames = ['usr','contact','name']

map(sql.Identifier, colnames)


temp = sql.SQL(', ').join(map(sql.Identifier, colnames))
temp2 = sql.SQL(', ').join((sql.Placeholder(), colnames))

'''
WITH input_rows(usr, contact, name) AS (
    VALUES ('Susan', 'susan@email.com',NULL),('Edward', 'ed@gmail.com', NULL)
    ),
    ins AS (INSERT INTO chats (usr, contact, name) SELECT * FROM input_rows
    ON CONFLICT (usr) DO NOTHING RETURNING id)
    SELECT 'inserted' AS source, id FROM ins  -- IDs of newly inserted rows
    UNION ALL (SELECT 'selected' AS source, chats.id FROM input_rows JOIN chats USING (usr));
'''



qs = "WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({}) SELECT * FROM input_rows ON CONFLICT (usr) DO NOTHING RETURNING id) SELECT 'inserted' AS source, id FROM ins UNION ALL (SELECT 'selected' AS source, chats.id FROM input_rows JOIN chats USING(usr))"

q = sql.SQL(qs).format(temp,temp2,sql.Identifier('chats'),temp)

q = sql.SQL("WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO chats({}) SELECT * FROM input_rows ON CONFLICT (usr) DO NOTHING RETURNING id) SELECT 'inserted' AS source, id FROM ins UNION ALL (SELECT 'selected' AS source, chats.id FROM input_rows JOIN chats USING(usr))").format(temp, temp2, temp)

q2 = "INSERT INTO {}({}) VALUES ({})"


d = values[2].split("T")[0].split("-")
d = list(map(int, d))

values[2] = datetime.date(d[0], d[1], d[2])


#q = sql.SQL("INSERT INTO chats({}) VALUES ({}) ON CONFLICT DO NOTHING RETURNING id").format(temp, temp2).as_string(conn)



key = 'articles'  # should be name of table

assert len(values) == len(TARGET_INFO[key])

table_name = sql.Identifier(key)
fields = sql.SQL(', ').join(map(sql.Identifier, TARGET_INFO[key]))
placeholders = sql.SQL(', ').join(map(sql.Placeholder, TARGET_INFO[key]))

q = sql.SQL(QUERIES[key]).format(fields, placeholders, table_name, fields)

q = 'WITH input_rows("feed_id", "headline", "date", "summary", "byline", "wordcount", "page_number", "url") AS (VALUES (%(feed_id)s, %(headline)s, %(date)s, %(summary)s, %(byline)s, %(wordcount)s, %(page_number)s, %(url)s)), ins AS (INSERT INTO "articles"("feed_id", "headline", "date", "summary", "byline", "wordcount", "page_number", "url") SELECT * FROM input_rows ON CONFLICT (url) DO NOTHING RETURNING id) SELECT \'inserted\' AS source, id FROM ins UNION ALL (SELECT \'selected\' AS source, articles.id FROM input_rows JOIN articles USING(url))'

with conn:
    with conn.cursor() as curs:
        curs.execute(q, values)
        article_ID = curs.fetchall()
        

def articleInsert(conn, target_info, queries, values):
    
    key = 'articles'  # should be name of table
    
    assert len(values) == len(target_info[key])
    
    table_name = sql.Identifier(key)
    fields = sql.SQL(', ').join(map(sql.Identifier, target_info[key]))
    placeholders = sql.SQL(', ').join(sql.Placeholder()*len(target_info[key]))
    
    q = sql.SQL(queries[key]).format(fields, placeholders, table_name, fields)
    
    with conn:
        with conn.cursor() as curs:
            curs.execute(q, values)
            article_ID = curs.fetchall()
            
    return article_ID

def place_mentionsInsert(conn, target_info, queries, values):
    
    key = 'place_mentions'
    
    assert len(values) == len(target_info[key])
    
    
    table_name = sql.Identifier(key)
    fields = sql.SQL(', ').join(map(sql.Identifier, target_info[key]))
    place_holders = sql.SQL(', ').join(sql.Placeholder()*len(target_info[key]))
    
    q = sql.SQL(queries[key]).format(table_name, fields, place_holders)
    
    with conn:
        with conn.cursor() as curs:
            curs.execute(q, values)
            
            
    
    
    






































with conn as con:
    with con.cursor() as curs:
        curs.execute(q, values[1])
        result = curs.fetchall()
        
        