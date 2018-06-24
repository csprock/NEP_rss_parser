import datetime
import re
import os
import sys

from nltk.tokenize import sent_tokenize
import feedparser



from entityFilter.searchFunctions import returnMatches
from entityFilter.makeGraphData import makeGraphData
from entityFilter.SearchGraph import SearchGraph

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..'))


from database_utils import execute_query
from database_utils import generate_article_query, generate_tag_query, generate_place_mentions_query


def make_place_filter(conn_obj, market_id):

    q = "SELECT place_name, place_id FROM places WHERE market_id = %s"

    with conn_obj as con:
        with con.cursor() as curs:
            curs.execute(q, (market_id,))
            results = curs.fetchall()

    R, _, E = makeGraphData([n[0] for n in results])
    G = SearchGraph(R, results, E)
    return G


def parse_entry(rss_entry):
    # need to add exception handling
    parsed_results = dict()
    try:
        parsed_results['id'] = rss_entry.id
    except:
        parsed_results['id'] = None

    parsed_results['title'] = rss_entry.title
    parsed_results['link'] = rss_entry.link
    parsed_results['summary'] = re.sub('<.*?>', '', rss_entry.summary)  # filter out HTML tags
    #parsed_results['content'] = re.sub('<.*?>', '', rss_entry.content[0]['value'])
    date_temp = rss_entry.published_parsed[:3]
    parsed_results['date'] = datetime.date(year = date_temp[0], month = date_temp[1], day = date_temp[2])

    return parsed_results



def generate_place_mention_info(parsed_results, G):
    '''
    Input
    -----
    parsed_result: dict
        dictionary with keys: id, title, link, summary, date. Generated by parse_entry
    G: SearchGraph

    Returns
    -------
    list of dict or None. If not None, list of dict with keys: place_id, context, loc
    '''

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


def generate_place_tag_info(place_mention_info):
    '''
    Input
    -----
    place_mention_info: list of dict
        results generated by generate_place_mention_info()

    Output
    ------
    list of unique int:
        unique place_id's of places matched in generate_place_mention_info()
    '''
    place_ids = list()
    for p in place_mention_info:
        place_ids.append(p['place_id'])

    return list(set(place_ids))



def get_info(parsed_result, feed_id, G):
    '''
    returns dictionary with values to insert into each table of DB

    '''

   # parsed_result = parse_entry(rss_entry)

    place_mention_info = generate_place_mention_info(parsed_result, G)

    if place_mention_info is not None:

        entry_info = dict()
        entry_info['place_tags'] = generate_place_tag_info(place_mention_info)
        entry_info['place_mentions'] = place_mention_info


        entry_info['articles'] = {k: parsed_result[k] for k in parsed_result if k in ['title','link','id','date','summary']}
        entry_info['articles']['feed_id'] = feed_id

#        article_info['feed_id'] = feed_id
#        article_info['headline'] = parsed_result['title']
#        article_info['url'] = parsed_result['link']
#        article_info['content_id'] = parsed_result['id']
#        article_info['date'] = parsed_result['date']
#        article_info['summary'] = parsed_result['summary']

        #entry_info['articles'] = article_info


        return entry_info
    else:
        return None


def parse_feed(rss_url, feed_id, G):

    rss_results = feedparser.parse(rss_url)

    if rss_results['bozo'] == 1:
        #print("WARN " + str(rss_results['bozo_exception']))
        raise ValueError("Connection error: " + str(rss_results['bozo_exception']))

    else:
        parsed_results = list()
        for entry in rss_results.entries:

            parsed_entry = get_info(parse_entry(entry), feed_id, G)
            if parsed_entry is not None:
                parsed_results.append(parsed_entry)

        return parsed_results


##### these functions are database schema dependent #####

def make_article_dict(entry_info):
    '''
    Returns dictionary whose keys match the field names in 'articles' table of database.
    '''

    article_dict = dict()
    article_dict['feed_id'] = entry_info['articles']['feed_id']
    article_dict['headline'] = entry_info['articles']['title']
    article_dict['url'] = entry_info['articles']['link']
    article_dict['content_id'] = entry_info['articles']['id']
    article_dict['date'] = entry_info['articles']['date']
    article_dict['summary'] = entry_info['articles']['summary']

    return article_dict


def make_tag_dict(entry_info, article_id):
    '''
    Returns list of dictionaries whose keys are the field names in the 'place_tags' table in database.
    '''
    place_tags_dict = list()
    for p in entry_info['place_tags']:
        place_tags_dict.append({'article_id':article_id, 'place_id':p})

    return place_tags_dict


def make_place_mentions_dict(entry_info, tag_id, place_id):
    '''
    Returns list of dictionaries whose keys are the field names in the 'place_mentions' table in database.
    '''
    place_mentions_dict = list()
    entries = list(filter(lambda x: x['place_id'] == place_id, entry_info['place_mentions']))

    for e in entries:
        place_mentions_dict.append({'tag_id':tag_id,'context':e['context'],'location':e['loc']})

    return place_mentions_dict



def execute_insertions(entry, conn):

    article_dict = make_article_dict(entry)
    q_article = generate_article_query(list(article_dict.keys()))

    results = execute_query(conn, q_article, data = article_dict, return_values = True)
    article_id = results[0][1]

    tag_dict = make_tag_dict(entry, article_id)
    q_tag = generate_tag_query(list(tag_dict[0].keys()))

    for tg in tag_dict:

        tag_results  = execute_query(conn, q_tag, data = tg, return_values = True)
        tag_id = tag_results[0][1]

        if tag_results[0][0] == 'inserted':

            place_id = tg['place_id']

            mentions_dict = make_place_mentions_dict(entry, tag_id, place_id)
            q_mention = generate_place_mentions_query(list(mentions_dict[0].keys()))

            for m in mentions_dict:
                execute_query(conn, q_mention, data = m)
