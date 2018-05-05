import datetime
import re
from nltk.tokenize import sent_tokenize
import feedparser
from entityFilter.searchFunctions import returnMatches



def entry_parser(rss_entry):
    
    parsed_results = dict()
    parsed_results['id'] = rss_entry.id
    parsed_results['title'] = rss_entry.title
    parsed_results['url'] = rss_entry.link
    parsed_results['summary'] = re.sub('<.*?>', '', rss_entry.summary)  # filter out HTML tags
    #parsed_results['content'] = re.sub('<.*?>', '', rss_entry.content[0]['value'])
    date_temp = rss_entry.published_parsed[:3]
    parsed_results['date'] = datetime.date(year = date_temp[0], month = date_temp[1], day = date_temp[2])

    return parsed_results
    


def generatePlaceMentionInfo(parsed_results, G):
    
    not_empty = False
    title_matches = returnMatches(G, parsed_results['title'], returnAll = False, returnType = 'id', id_only = True)
    
    title_place_mentions_info = list()
    if len(title_matches) > 0:
        not_empty = True
        for i in title_matches:
            title_place_mentions_info.append({'place_id':i, 'context':parsed_results['title'], 'loc':'title'})
        
        
    
    summary_sentences = sent_tokenize(parsed_results['summary'])
    summary_place_mentions_tuples = list()
    
    for s in summary_sentences:
        
        matches = returnMatches(G, s, returnAll = False, returnType = 'id', id_only = True)
        if len(matches) > 0:
            not_empty = True

            for i in matches:
                summary_place_mentions_tuples.append({'place_id':i, 'context':s, 'loc':'summary'})
                
    if not_empty:
        return title_place_mentions_info + summary_place_mentions_tuples
    else:
        return None
    
# takes output of generatePlaceMentionInfo()
def generatePlaceTagInfo(place_mention_info):
    
    place_ids = list()
    for p in place_mention_info:
        place_ids.append(p['place_id'])
        
    return list(set(place_ids))



def getInfo(rss_entry, feed_id, G):
    
    parsed_result = entry_parser(rss_entry)
    
    place_mention_info = generatePlaceMentionInfo(parsed_result, G)
    if place_mention_info is not None:
        place_tag_info = generatePlaceTagInfo(place_mention_info)
        
        article_info = dict()
        article_info['feed_id'] = feed_id
        article_info['headline'] = parsed_result['title']
        article_info['url'] = parsed_result['link']
        article_info['content_id'] = parsed_result['id']
        article_info['date'] = parsed_result['date']
        article_info['summary'] = parsed_result['summary']
        
        entry_info = dict()
        entry_info['articles'] = article_info
        entry_info['place_tags'] = place_tag_info
        entry_info['place_mentions'] = place_mention_info
        
        return entry_info
    else:
        return None
        




def makeArticleDict(entry_info):
    
    article_dict = entry_info['articles']
    return article_dict

def makeTagDict(entry_info, article_id):
    place_tags_dict = list()
    for p in entry_info['place_tags']:
        place_tags_dict.append({'article_id':article_id, 'place_id':p})
        
    return place_tags_dict


def makeMentionsDict(entry_info, tag_id, place_id):
    
    place_mentions_dict = list()
    entries = list(filter(lambda x: x['place_id'] == place_id, entry_info['place_mentions']))
    
    for e in entries:
        
        place_mentions_dict.append({'tag_id':tag_id, 
                                    'context':entry_info['place_mentions']['context'],
                                    'location':entry_info['place_mentions']['loc']})
    
    return place_mentions_dict



def parse_feed(rss_url, feed_id, G):
    
    rss_results = feedparser.parse(rss_url)
    
    if rss_results['bozo'] == 1:
        print("WARN " + str(rss_results['bozo_exception']))
    else:
        
        parsed_results = list()
        for entry in rss_results.entries:
            parsed_entry = getInfo(entry, feed_id, G)
            if parsed_entry is not None:
                parsed_results.append(parsed_entry)
                
        return parsed_results     


class databaseInserter:
    
    

    def __init__(self, conn_info):
        
        self.CONN = connectToDatabase(conn_info)
        
        self.base_query_1 = '''
        WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({}) 
        SELECT * FROM input_rows ON CONFLICT (url) DO NOTHING RETURNING id) 
        SELECT 'inserted' AS source, id FROM ins UNION ALL 
        (SELECT 'selected' AS source, {}.id FROM input_rows JOIN {} USING(url))
        '''
        
        self.base_query_2 = "INSERT INTO {}({}) VALUES ({})"
        
        self.duplicates = []
        
        
        
    def _generateSQL_1(self, values):
    
        f_dict = {k:v for k, v in values.items() if v != None}
        
        field_names = f_dict.keys()
        
        # create SQL variables
        table_name = sql.Identifier('articles')
        fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
        placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))
        
        # feed variables to psycopg2's sql statement formatter
        q = sql.SQL(self.base_query_1).format(fields, placeholders, table_name, fields, table_name, table_name)
        return q
    

    def _generateSQL_2(self, values):
    
        field_names = values.keys()
        
        # create SQL variables
        table_name = sql.Identifier('place_mentions')
        fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
        placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))
        
        # feed variables to psycopg2's sql statement formatter
        q = sql.SQL(self.base_query_2).format(table_name, fields, placeholders)
        return q
    
    
        
    def executeInsertion(self, feed_id, place_id, data):
        
        valueTuple1 = makeArticleTuple(feed_id, data, as_dict = True)
        q1 = self._generateSQL_1(valueTuple1)
        
        with self.CONN as conn:
            with conn.cursor() as curs:
                curs.execute(q1, valueTuple1)
                returned_id = curs.fetchall()
                
        
        if returned_id[0][0] == 'selected':
            print("Duplicate found at article_id: %s" % str(returned_id[0][1]))
            self.duplicates.append((returned_id[0][1], place_id))
            
            
        
        valueTuple2 = makePlaceMentionsTuple(returned_id[0][1], place_id, as_dict = True)
        q2 = self._generateSQL_2(valueTuple2)
        
        with self.CONN as conn:
            with conn.cursor() as curs:
                curs.execute(q2, valueTuple2)
                
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    