import datetime
import time
import os
import sys
import json

mypath = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(os.path.join(mypath, os.path.pardir))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), 'nytScraper'))

from database_utils import execute_query
from database_utils import generate_article_query, generate_tag_query, generate_keyword_query
from results_parser import process_results
from articleAPI import articleAPI


class KEYRING:
    """
    Object to be used in getResults().

    Class for storing API keys. Used by getResults() to track which keys have reached their download limits.
    Contains accessor methods for updating keys status and for returning the next usable key.
    """


    def __init__(self, key):

        self.KEYS = dict()

        if isinstance(key, str):
            self.Keys[key] = True
        elif isinstance(key, list):
            for k in key:
                assert isinstance(k, str)
                self.KEYS[k] = True
        else:
            raise ValueError("KEYRING object must be initialized by a string or list of strings.")


    def status(self):
        if True in self.KEYS.values():
            return True
        else:
            return False


    def updateStatus(self, key, val):
        self.KEYS[key] = val


    def nextKey(self):
        trues = []
        for i , val in enumerate(self.KEYS.values()):
            if val is True:
                trues.append(i)

        if len(trues) > 0:
            return list(self.KEYS.keys())[trues[0]]
        else:
            return None


#keyring = KEYRING(API_KEYS)
#
#keyring.checkKeys()
#keyring.updateStatus('d7117d6c63404420b03ee92aa4ec9806', False)

def execute_api_query(api_obj, verbose = False, **kwargs):

    """
    Is a wrapper function for the articleAPI.search() function that parses return messages
    and errors. This function takes the articleAPI object and the arguments to be passed to the object.
    The arguments are passed to the articleAPI.search() function and the results of the function parsed.
    A dictionary containing the information about status messages and the test_data if the query execution
    was successful.

    Data returned by the API is processed by the process_results() function and returned as a

    Performs following checks:
        - checks the return status of the packet
        - checks the number of hits
        - checks if API limit rate has been exceeded
        - checks if any other error occured

    Parameters
    ----------
    api_obj: articleAPI search object


    kwargs
    ------
    query parameters to be passed to the articleAPI.search() function.


    Returns
    -------
    status: bool
        returns True when there are results to parse.
    output_data: list of dict or None
        list of dict returned by process_results() or None if no results or unsuccessful query
    api_limit: bool
        True if API limit rate exceeded
    hits: int
        number of returned search hits

    """

    output_status = bool()
    output_data = None
    api_limit = False
    hits = None

    # execute the API query
    results = api_obj.search(**kwargs)      # returns the result of a requests.get() function

    # parse results of query
    try:

        status = results['status']

        if status == 'ERROR':
            output_status = False
            print("Warning: Error " + results['errors'][0])

        elif status == 'OK':

            hits = int(results['response']['meta']['hits'])

            if hits == 0:
                output_status = False
                if verbose: print("No results found.")

            else:
                output_status = True
                #output_data = results['response']['docs']
                output_data = process_results(results)
        else:
            output_status = False
            if verbose: print("Error")


    except KeyError:
        output_status = False

        # checks for message in the return packet
        if results['message'] == 'API rate limit exceeded':
            if verbose: print(results['message'])
            api_limit = True
        else:
            if verbose: print(results['message'])


    return {'status':output_status, 'api_status': api_limit, 'test_data':output_data, 'hits': hits}

class nytScraper:

    def __init__(self, key):
        self.KEYRING = KEYRING(key)

    def run_query(self, page_range, verbose = False, **kwargs):

        if isinstance(page_range, list):
            current_page, stop_page = page_range[0], page_range[1]
        elif page_range == 'all':
            current_page, stop_page = 0, 200
        else:
            raise ValueError("Must supply list of form [start_page, end_page] or 'all'.")

        # initialize variables
        current_key = self.KEYRING.nextKey()             # set current API key to use
        api_obj = articleAPI(current_key)                # initialize articleAPI object using current_key

        results_list = list()                            # initialize list where results of queries will be stored


        # Check the number of hits and the number of pages needed to download all of them.
        # If number of pages exceeds maximum allowed by the API (200), returns exception.
        #kwargs['page']  = current_page
        results = execute_api_query(api_obj, page = current_page, **kwargs)
        hits = results['hits']

        if hits == 0 or hits == None:
            return None

        hits_pages = hits // 10

        if hits_pages > 200:
            raise ValueError("The number of pages will exceed 200! Number of hits is " + str(hits))
        else:
            if verbose: print("Number of results pages: " + str(hits_pages) + " Number of hits: " + str(hits))


        while True: # loop runs until stop condition breaks it

            # patch to fix expanding string bug inside fq and other dictionary kwargs
            # does not effect string kwargs
            for k in kwargs.keys():
                if isinstance(kwargs[k], dict):
                    for u in kwargs[k].keys():
                        if isinstance(kwargs[k][u], str):
                            kwargs[k][u] = kwargs[k][u].replace('"', '').strip()


            time.sleep(1)

            results = execute_api_query(api_obj, page = current_page, **kwargs)

            if results['status'] == True:

                results_list.extend(results['test_data'])
                if verbose: print("Status: OK. Current page: " + str(current_page))
                current_page += 1

            else:
                # check API status, if API limit reached set status of current key to False and update current key
                # If all keys have reached their limits, print message and break.

                if results['api_status']:
                    self.KEYRING.updateStatus(current_key, False)

                    # if there is another usable key, set current_key to this key otherwise breaks main loop.
                    if self.KEYRING.status():
                        current_key = self.KEYRING.nextKey()
                        api_obj = articleAPI(current_key)

                    else:
                        if verbose: print("All API keys have reached their limits.")
                        break


            if current_page > min([hits_pages, stop_page]):
                break

        return results_list


def generate_dates():

    def _datestr(date_object):

        year = str(date_object.year)
        month = str(date_object.month)
        day = str(date_object.day)

        if len(day) == 1:
            day = '0' + day
        if len(month) == 1:
            month = '0' + month

        return year + month + day

    today = datetime.date.today()
    dt = datetime.timedelta(days = 1)
    yesterday = today - dt

    return _datestr(today), _datestr(yesterday)

###############################################################################
# the following functions are specific to the database schema and will have
# to be updated if the database is updated


def make_article_tuple(feed_id, data, as_dict = False):

    date_parts = list(map(int, data['date'].split("-")))


    if as_dict:
        output = dict()
        output['feed_id'] = feed_id
        output['headline'] = data['headline']
        output['date'] = datetime.date(date_parts[0], date_parts[1], date_parts[2])
        output['summary'] = data['snippet']
        output['content_id'] = data['id']
        output['url'] = data['url']

        try:
            output['wordcount'] = int(data['word_count'])
        except:
            pass

        try:
            output['page_number'] = int(data['page'])
        except:
            pass

    else:
        output = (feed_id,
                    data['id'],
                    data['headline'],
                    datetime.date(date_parts[0],date_parts[1],date_parts[2]),
                    data['snippet'],
                    data['word_count'],
                    data['page'],
                    data['url'])

    return output



def make_place_tag_tuple(article_id, place_id, as_dict = False):

    if as_dict:
        output = dict()
        output['article_id'] = article_id
        output['place_id'] = place_id
    else:
        output = (article_id, place_id)

    return output


def make_keyword_tuples(article_id, data, as_dict = False):

    output = list()

    if as_dict:
        for kw in data['keywords']:
            output.append(dict(article_id = article_id, tag = kw[0], keyword = kw[1]))
    else:
        for kw in data['keywords']:
            output.append((article_id, kw[0], kw[1]))

    return output


def execute_insertions_nyt(conn, data, feed_id, place_id):
    # connection, test_data, feed_id (for NYT API), place_id

    article_dict = make_article_tuple(feed_id, data, as_dict = True)
    q_article = generate_article_query(list(article_dict.keys()))

    results = execute_query(conn, q_article, data = article_dict, return_values = True)
    article_id = results[0][1]

    tag_dict = make_place_tag_tuple(article_id, place_id, as_dict = True)
    q_tag = generate_tag_query(list(tag_dict.keys()))

    execute_query(conn, q_tag, data = tag_dict, return_values = False)

    keyword_dicts = make_keyword_tuples(article_id, data, as_dict = True)
    if len(keyword_dicts) > 0:
        q_keyword = generate_keyword_query(list(keyword_dicts[0].keys()))
        for k in keyword_dicts:
            execute_query(conn, q_keyword, data = k, return_values = False)




def execute_api_search(scraper, place_list, market_id, yesterday, today):

    results, rejects = list(), list()
    for p in place_list:
        place_name, place_id = p[0], p[1]
        time.sleep(1)

        try:
            r = scraper.run_query(page_range = 'all', q = '"' + place_name + '"', fq = {'glocations':'New York City'}, begin_date = yesterday , end_date = today)
            results.append( dict( place_id = place_id, query_results = r))
        except json.JSONDecodeError:
            rejects.append((place_name, place_id))

    # filter out empty results
    results = list(filter(lambda x: x['query_results'] != None, results))
    # format rejected queries for JSON storage
    if len(rejects) > 0:
        rejects = {'dates':{'yesterday':yesterday, 'today':today},
                    'place_list':rejects}
    else:
        rejects = None

    return results, rejects



#def _json_bytify(test_data, ignore_dicts = False):
#
#    if isinstance(test_data, unicode):
#        return test_data.encode('utf-8')
#
#    if isinstance(test_data, list):
#        return [_json_bytify(d, ignore_dicts = True) for d in test_data]
#
#    if isinstance(test_data, dict) and not ignore_dicts:
#        return {_json_bytify(k, ignore_dicts = True): _json_bytify(v, ignore_dicts = True) for k, v in test_data.items()}
#
#    return test_data
#
#def json_load_bytes(f):
#    return _json_bytify(json.load(f, object_hook = _json_bytify), ignore_dicts = True)
#



#class databaseInserter:
#
#
#
#    def __init__(self, conn_info):
#
#        self.CONN = connect_to_database(conn_info)
#
#        self.base_query_1 = '''
#        WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({})
#        SELECT * FROM input_rows ON CONFLICT (url) DO NOTHING RETURNING id)
#        SELECT 'inserted' AS source, id FROM ins UNION ALL
#        (SELECT 'selected' AS source, {}.id FROM input_rows JOIN {} USING(url))
#        '''
#
#        self.base_query_2 = "INSERT INTO {}({}) VALUES ({})"
#
#        self.duplicates = []
#
#
#
#    def _generateSQL_1(self, values):
#
#        f_dict = {k:v for k, v in values.items() if v != None}
#
#        field_names = f_dict.keys()
#
#        # create SQL variables
#        table_name = sql.Identifier('articles')
#        fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
#        placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))
#
#        # feed variables to psycopg2's sql statement formatter
#        q = sql.SQL(self.base_query_1).format(fields, placeholders, table_name, fields, table_name, table_name)
#        return q
#
#
#    def _generateSQL_2(self, values):
#
#        field_names = values.keys()
#
#        # create SQL variables
#        table_name = sql.Identifier('place_mentions')
#        fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
#        placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))
#
#        # feed variables to psycopg2's sql statement formatter
#        q = sql.SQL(self.base_query_2).format(table_name, fields, placeholders)
#        return q
#
#
#
#    def executeInsertion(self, feed_id, place_id, test_data):
#
#        valueTuple1 = make_article_tuple(feed_id, test_data, as_dict = True)
#        q1 = self._generateSQL_1(valueTuple1)
#
#        with self.CONN as conn:
#            with conn.cursor() as curs:
#                curs.execute(q1, valueTuple1)
#                returned_id = curs.fetchall()
#
#
#        if returned_id[0][0] == 'selected':
#            print("Duplicate found at article_id: %s" % str(returned_id[0][1]))
#            self.duplicates.append((returned_id[0][1], place_id))
#
#
#
#        valueTuple2 = make_place_tag_tuple(returned_id[0][1], place_id, as_dict = True)
#        q2 = self._generateSQL_2(valueTuple2)
#
#        with self.CONN as conn:
#            with conn.cursor() as curs:
#                curs.execute(q2, valueTuple2)
