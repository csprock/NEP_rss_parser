import re
import feedparser
import datetime
import psycopg2
from placeFilter import *
from rss_config import connectToDatabase
from createFilterList import createFilterList


def getPlaceList(region_id, conn_obj):
    
    with conn_obj as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT place FROM place WHERE county_fips IN (SELECT county_fips FROM regions_to_county WHERE region_id = %s);", (region_id,))
            place = cur.fetchall()
    
    with conn_obj as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT county FROM county WHERE county_fips IN (SELECT county_fips FROM regions_to_county WHERE region_id = %s)", (region_id,))
            county = cur.fetchall()
            
            
    cur = conn.cursor()
    
    place.extend(county)
    return [p[0] for p in place]


def makeFilter(region_id, conn_obj):
    place_list = getPlaceList(region_id, conn_obj)
    filter_list = createFilterList(place_list)
    return placeFilter(filter_list)



class processRSS:
    
    FILTER = None
    
    def __init__(self, filterObj):
        assert isinstance(filterObj, placeFilter)
        
        self.FILTER = filterObj
        
    def parse_feed(self, rss_url):
                
        results = feedparser.parse(rss_url)
        
        
        parsed_entries = []
        for entry in results.entries:
            parsed = self._filter_entry(entry)
            if parsed != None:
                parsed_entries.append(parsed)
        
        ### print error warnings ###
        if results['bozo'] == 1:
            print("WARN: " + str(results['bozo_exception']))
        
        return parsed_entries    

    def _entry_parser(self, rss_entry):
        
        # need to add error handling
        parsed_results = dict()
        parsed_results['id'] = rss_entry.id
        parsed_results['title'] = rss_entry.title
        parsed_results['url'] = rss_entry.link
        parsed_results['summary'] = re.sub('<.*?>', '', rss_entry.summary)  # filter out HTML tags
        parsed_results['content'] = re.sub('<.*?>', '', rss_entry.content[0]['value'])
        date_temp = rss_entry.published_parsed[:3]
        parsed_results['date'] = datetime.date(year = date_temp[0], month = date_temp[1], day = date_temp[2])
    
        return parsed_results
    
    
    
    def _filter_entry(self, rss_entry):
        
        parsed_entry = self._entry_parser(rss_entry)
        textblob = " ".join([parsed_entry['title'], parsed_entry['content']])
        place_list = self.FILTER.checkFilters(textblob)
        
        if len(place_list) > 0:
            return {'entry':parsed_entry, 'places':place_list}
        else:
            return None
        
        
############# RSS feed parsing functions ###############
#def entry_parser(rss_entry):
#    
#    # need to add error handling
#    parsed_results = dict()
#    parsed_results['id'] = rss_entry.id
#    parsed_results['title'] = rss_entry.title
#    parsed_results['url'] = rss_entry.link
#    parsed_results['summary'] = re.sub('<.*?>', '', rss_entry.summary)  # filter out HTML tags
#    parsed_results['content'] = re.sub('<.*?>', '', rss_entry.content[0]['value'])
#    date_temp = rss_entry.published_parsed[:3]
#    parsed_results['date'] = datetime.date(year = date_temp[0], month = date_temp[1], day = date_temp[2])
#
#    return parsed_results
#
#
#def filter_entry(rss_entry, place_filter):
#    
#    parsed_entry = entry_parser(rss_entry)
#    textblob = " ".join([parsed_entry['title'], parsed_entry['content'], parsed_entry['summary']])
#    place_list = place_filter.checkFilters(textblob)
#    
#    if len(place_list) > 0:
#        return {'entry':parsed_entry, 'places':place_list}
#    else:
#        return None
#
#
#def parse_feed(rss_url, place_filter):
#    
#    assert isinstance(place_filter, placeFilter) == True
#    
#    results = feedparser.parse(rss_url)
#    
#    parsed_entries = []
#    for entry in results.entries:
#        parsed = filter_entry(entry, place_filter)
#        if parsed != None:
#            parsed_entries.append(parsed)
#    
#    return parsed_entries
            

######### write to database ###########

class writeToArticleDB:
    
    conn = None
    feed_id = int()
    
    def __init__(self, conn_info, feed_id):
        assert isinstance(conn_info, dict)
        assert isinstance(feed_id, int)
        
        self.feed_id = feed_id
        self.conn = connectToDatabase(conn_info, False)
        

    def _writeArticle(self, data):
        
        data.update({'feed_id':self.feed_id})
        
        with self.conn as conn:
            with conn.cursor() as curs:
                
                q = "INSERT INTO article (feed_id, content_id, title, date, summary, url) VALUES (%(feed_id)s, %(id)s, %(title)s, %(date)s, %(summary)s, %(url)s) RETURNING id;"
                curs.execute(q, data)
                return  curs.fetchone()
                
    
    
    def _writePlace(self, data, article_id):
        
        q = "INSERT INTO place_tags (article_id, place) VALUES (%s,%s);"
        with self.conn as conn:
            with conn.cursor() as curs:
                for d in data:
                    curs.execute(q, (article_id, d))

    
    
    def writeToDatabase(self, data):
        
        try:
            article_id = self._writeArticle(data['entry'])
            self._writePlace(data['places'], article_id)
        except psycopg2.IntegrityError:
            pass


#def writeArticle(data, feed_id, conn_object):
#    
#    data.update({'feed_id':feed_id})
#    
#    with conn_object:
#        with conn_object.cursor() as curs:
#            
#            q = "INSERT INTO article (feed_id, content_id, title, date, summary, url) VALUES (%(feed_id)s, %(id)s, %(title)s, %(date)s, %(summary)s, %(url)s) RETURNING id;"
#            curs.execute(q, data)
#            return  curs.fetchone()
#            
#
#
#def writePlace(data, article_id, conn_object):
#    
#    q = "INSERT INTO place (article_id, place) VALUES (%s,%s);"
#    with conn_object:
#        with conn_object.cursor() as curs:
#            for d in data:
#                curs.execute(q, (article_id, d))
#                
#    
#    
#    
#def writeToDatabase(data, feed_id, conn_obj):
#    
#    try:
#        article_id = writeArticle(data['entry'], feed_id, conn_obj)
#        writePlace(data['places'], article_id, conn_obj)
#    except psycopg2.IntegrityError:
#        pass
#    