import psycopg2
from psycopg2 import sql
import pandas as pd

CONN_INFO = {'dbname':'rss_feed_2', 'username':'postgres','password':'redalert'}

conn_obj = connectToDatabase(CONN_INFO)




with conn_obj as conn:
    with conn.cursor() as cur:
        cur.execute(q, ("Portland Zone",))
        t = cur.fetchone()


########################## add a region to database ###########################

def addPlaceName(place_name, table_name, conn_obj):
    
    q = sql.SQL(
            "INSERT INTO {} (place_name) VALUES (%s) RETURNING place_id"
            ).format(sql.Identifier(table_name))
    
    with conn_obj as conn:
        with conn.cursor() as cur:
            cur.execute(q, (place_name,))
            i = cur.fetchone()
            
    return i[0]


def addRegionName(place_id, place_name, table_name, conn_obj):
    
    q = sql.SQL("INSERT INTO {} (place_id, region_name) VALUES (%s,%s)"
                ).format(sql.Identifier(table_name))
    
    with conn_obj as conn:
        with conn.cursor() as cur:
            cur.execute(q, (place_id, place_name))
            
            

def addRegion(region_name, CONN_INFO):
    
    conn = connectToDatabase(CONN_INFO)
    
    i = addPlaceName(region_name, "place_names", conn)
    addRegionName(i, region_name, "regions", conn)
    conn.close()


###################### add a subregion to database #####################
    
def addSubRegionName(place_id, place_name, table_name, conn_obj):
    
    q = sql.SQL("INSERT INTO {} (place_id, subregion_name) VALUES (%s,%s) RETURNING subregion_id"
                ).format(sql.Identifier(table_name))
    
    with conn_obj as conn:
        with conn.cursor() as cur:
            cur.execute(q, (place_id, place_name))
            i = cur.fetchone()
    
    return i[0]


            
            
def addRelationship(subregion_id, region_name, region_table, table_name, conn_obj):
    
    # fetch region_id
    q1 = sql.SQL("SELECT region_id FROM {} WHERE region_name = %s").format(sql.Identifier(region_table))
    with conn_obj as conn:
        with conn.cursor() as cur:
            cur.execute(q1, (region_name,))
            t = cur.fetchone()
            
    
    
    q = sql.SQL("INSERT INTO {} (region_id, subregion_id) VALUES (%s,%s)").format(sql.Identifier(table_name))
    
    with conn_obj as conn:
        with conn.cursor() as cur:
            cur.execute(q, (subregion_id, t))






















    