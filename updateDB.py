import psycopg2
from placeFilter import placeFilter
from rss_config import CONN_INFO, connectToDatabase
from createFilterList import createFilterList
from RSS_parser import processRSS, writeToArticleDB, makeFilter


def updateSource(r, conn_obj):
    
    source = r[0]
    region_id = r[1]
        
    filter_obj = makeFilter(region_id, conn_obj)
    
    with conn_obj as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM feeds WHERE source = %s;", (source,))
            the_feeds = curs.fetchall()
        
    print("Source: %s" % source)
    processor = processRSS(filter_obj)
    
    for feed in the_feeds:
        url = feed[3]
        feed_id = feed[0]
        query_results = processor.parse_feed(url)
        writer = writeToArticleDB(CONN_INFO, feed_id)
        
        print("%s results returned for Feed %s" % (len(query_results), feed_id))
        
        for i, r in enumerate(query_results):
            writer.writeToDatabase(r)
        
        
        

#### update database ####

conn = connectToDatabase(CONN_INFO, False)
with conn:
    with conn.cursor() as curs:
        curs.execute("SELECT * FROM sources;")
        filter_info = curs.fetchall()
        


for f in filter_info:
    updateSource(f, conn)