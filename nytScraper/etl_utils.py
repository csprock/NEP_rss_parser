import datetime
import time
import os
import sys
import json
import logging

mypath = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(os.path.join(mypath, os.path.pardir))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), 'nytScraper'))

LOGGER = logging.getLogger(__file__)

log_formatter = logging.Formatter("[%(levelname)s] (%(asctime)s) %(message)s")

stream_handler = logging.StreamHandler()
LOGGER.setLevel(logging.DEBUG)
stream_handler.setFormatter(log_formatter)

LOGGER.addHandler(stream_handler)

from database_utils import execute_query
from database_utils import generate_article_query, generate_tag_query, generate_keyword_query
from results_parser import process_results
from results_parser import make_article_tuple, make_place_tag_tuple, make_keyword_tuples
from articleAPI import articleAPI

# Z5nXobB2H0cCDHL74zt88e0kiw5ZrFpt

class APIError(Exception):
    ''' Generic NYT API exception '''

    def __init__(self, msg=None, *args):
        if msg is None:
            msg = "Unknown API error."

        super().__init__(msg, *args)


class APILimitRate(APIError):
    default_msg = '''API Limit Rate Exceeded.'''

    def __init__(self, msg=default_msg, *args):
        super().__init__(msg, *args)


class NoResults(APIError):
    default_msg = '''No results found.'''

    def __init__(self, msg=default_msg, *args):
        super().__init__(msg, *args)


class InvalidAPIKey(APIError):
    '''Invalid API keys'''

    def __init__(self, msg, key):
        super().__init__(msg, key)


class AllLimitsReached(APIError):
    ''' All API keys have reached limits'''

    def __init__(self, msg):
        super().__init__(msg)


class KEYRING:
    """
    Object to be used in getResults().

    Class for storing API keys. Used by getResults() to track which keys have reached their download limits.
    Contains accessor methods for updating keys status and for returning the next usable key.
    """

    def __init__(self, key):

        self.KEYS = dict()

        if isinstance(key, str):
            self.KEYS[key] = True
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


def check_results(results, api_key):
    '''
    Check the results of articleAPI.search(), raise exceptions
    if problems are found. Otherwise returns the results.

    :param results: raw output of articleAPI.search()
    :return: same as input unless exceptions are raised
    '''

    status = results.get('status')

    # check status
    if status is not None:

        if status == 'OK':
            # check number of hits
            hits = results['response']['meta']['hits']

            if hits > 0:
                return results
            else:
                raise NoResults

        elif status == 'ERROR':

            error = results.get('errors')
            raise APIError(error)

        else:
            raise APIError("Unknown Status: {}".format(status))

    else:

        fault = results.get('fault')

        if fault is not None:

            errorcode = fault['detail']['errorcode']

            if errorcode == 'policies.ratelimit.QuotaViolation':
                raise APILimitRate
            elif errorcode == 'oauth.v2.InvalidApiKey':
                raise InvalidAPIKey(errorcode, api_key)
            else:
                raise APIError(errorcode)

        else:
            raise APIError


class nytScraper:

    def __init__(self, key):
        self.KEYRING = KEYRING(key)

    def run_query(self, start_page=0, stop_page=200, **kwargs):
        '''

        :param start_page: start API results page
        :param stop_page: end API results page
        :param kwargs: passed onto articleAPI.search()
        :return:
        '''

        # initialize variables
        current_key = self.KEYRING.nextKey()             # set current API key to use
        api_obj = articleAPI(current_key)                # initialize articleAPI object using current_key

        results_list = list()                            # initialize list where results of queries will be stored
        current_page = start_page
        i = 0
        while True:

            # patch to fix expanding string bug inside fq and other dictionary kwargs
            # does not effect string kwargs
            for k in kwargs.keys():
                if isinstance(kwargs[k], dict):
                    for u in kwargs[k].keys():
                        if isinstance(kwargs[k][u], str):
                            kwargs[k][u] = kwargs[k][u].replace('"', '').strip()


            time.sleep(7)

            results = api_obj.search(page=current_page, **kwargs)

            try:
                results = check_results(results, current_key)

            # TODO: find out if there is a different errorcode for maximum requests reached
            except APILimitRate:

                self.KEYRING.updateStatus(current_key, False)

                if self.KEYRING.status():
                    current_key = self.KEYRING.nextKey()
                    api_obj = articleAPI(current_key)
                else:
                    raise AllLimitsReached

            # except NoResults:
            #     # TODO: catch this exception in next level up
            #     raise NoResults
            #
            # except InvalidAPIKey as e:
            #
            #     errorcode = e.args[0]
            #     key = e.args[1]
            #
            #     self.KEYRING.updateStatus(current_key, False)
            #
            #
            #     # TODO: catch next level up
            #
            #     raise InvalidAPIKey(errorcode, key)
            #
            # except APIError as e:
            #     # TODO: catch this exception in next level up
            #     raise APIError(e.args)

            else:
                try:
                    hits = results['response']['meta']['hits']
                    pages = hits // 10
                    #LOGGER.info("Number of results pages: " + str(pages) + ". Number of hits: " + str(hits))
                    LOGGER.debug("Page: {}".format(i))
                    i += 1

                    results_list.extend(results['response']['docs'])
                    current_page += 1

                    if current_page > min([pages, stop_page]):
                        return results_list
                except Exception as e:
                    LOGGER.exception(e)
                    return results



def execute_api_search(scraper, place_list, market_id, begin_date, end_date):

    all_results, rejects = list(), list()
    for p in place_list:
        place_name, place_id = p[0], p[1]
        time.sleep(1)

        try:

            results = scraper.run_query(begin_date=begin_date,
                                        end_date=end_date,
                                        q='"' + place_name + '"',
                                        fq={'glocations': 'New York City'})

            if results is None:
                LOGGER.debug("Returned null result set.")
                raise NoResults

        except NoResults:
            pass
        except InvalidAPIKey as e:
            msg = e.args[0]
            key = e.args[1]

            LOGGER.critical("{} - {}".format(msg, key))
            scraper.KEYRING.updateStatus(key, False)
            # TODO: add current job to queue

        except AllLimitsReached:
            LOGGER.info("All API keys have reached their limits.")
            # TODO: add remaining jobs to queue
            break
        except APIError as e:
            LOGGER.error(e.msg[0])

        except json.JSONDecodeError:
            LOGGER.error("Error decoding response.")
            # TODO: add current job to queue

        else:
            # filter out empty results
            results = list(filter(lambda x: x['query_results'] != None, results))
            if len(results) > 0:
                all_results.append(dict(place_id=place_id, query_results=results))

    return results



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


#########################################################################################

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
