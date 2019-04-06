import datetime
import time
import os
import sys
import json
import logging
from requests.exceptions import ConnectionError
import psycopg2

import redis

mypath = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(os.path.join(mypath, os.path.pardir))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), 'nyt_scraper'))

from database_utils import execute_query, execute_query2
from database_utils import generate_article_query, generate_tag_query, generate_keyword_query, generate_place_mentions_query
from nyt_scraper.results_parser import make_article_tuple, make_place_tag_tuple, make_keyword_tuples
from nyt_scraper.articleAPI import articleAPI
from nyt_scraper.results_parser import process_results

LOGGER = logging.getLogger('etl.etl_utils')

REQUEST_INTERVAL = float(os.environ['NYT_API_REQUEST_INTERVAL'])

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

    def __init__(self, *args):
        super().__init__(*args)


class KEYRING:

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
            raise AllLimitsReached("All API keys have reached their limits.")


def check_results(r, api_key):
    '''
    Check the results of articleAPI.search(), raise exceptions
    if problems are found. Otherwise returns the results.

    :param results: raw output of articleAPI.search()
    :param api_key: current API key
    :return: same as input unless exceptions are raised
    '''

    status_code = r.status_code
    results = r.json()

    if status_code == 200:

        status = results.get('status')

        # check status
        if status is not None:

            if status == 'OK':
                # check number of hits
                hits = results['response']['meta']['hits']

                if hits == 0:
                    raise NoResults

            elif status == 'ERROR':

                # ['page: must be less than or equal to 200'] is the return for page maxout
                error = results.get('errors')
                raise APIError(error[0], status_code)

            else:
                raise APIError("Unknown Status: {}".format(status))
        else:
            LOGGER.critical("Schema change detected in results['status'].")
            raise APIError("Unknown API Error.")

    elif status_code == 401:

        errorcode = None

        try:
            errorcode = results['fault']['detail']['errorcode']
        except KeyError:
            LOGGER.critical("Schema change detected in results['fault']['detail']['errorcode']")
        finally:
            raise InvalidAPIKey(str(status_code) + errorcode, api_key)

    elif status_code == 429:

        errorcode = None

        try:
            errorcode = results['fault']['detail']['errorcode']
        except KeyError:
            LOGGER.critical("Schema change detected in results['fault']['detail']['errorcode']")
        finally:
            raise APILimitRate(str(status_code) + errorcode)

    elif status_code == 400:
        raise APIError("400 Error")

    else:
        raise APIError("Unknown Error, Status Code: {}".format(status_code))


class NYTScraper:

    def __init__(self, key, conn=None):
        self.KEYRING = KEYRING(key)
        self.redis_conn = conn
        self.current_job = None

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

            time.sleep(REQUEST_INTERVAL)

            try:
                results = api_obj.search(page=current_page, **kwargs)
            except ConnectionError as e:
                LOGGER.warning(e)
                time.sleep(5)
            else:
                try:
                    check_results(results, current_key)
                    results = results.json()

                except APILimitRate:
                    self.KEYRING.updateStatus(current_key, False)
                    if self.KEYRING.status():
                        current_key = self.KEYRING.nextKey()
                        api_obj = articleAPI(current_key)
                        LOGGER.warning("API key reached limit, cycling new key.")
                    else:
                        raise AllLimitsReached("All API keys have reached their limits.")
                else:

                    try:
                        hits = results['response']['meta']['hits']
                        pages = hits // 10
                        LOGGER.debug("Page: {}".format(current_page))

                        parsed_results = process_results(results)
                        results_list.extend(parsed_results)
                        current_page += 1

                        if current_page > min([pages, stop_page]):
                            return results_list
                    except Exception as e:
                        LOGGER.exception(e)
                        raise

    def execute_api_search(self):

        all_results = list()

        rem_jobs = 1

        while rem_jobs > 0:

            self.current_job = json.loads(self.redis_conn.rpop('queue'))
            rem_jobs = self.redis_conn.llen('queue')
            LOGGER.debug(self.current_job)

            time.sleep(1)

            try:

                results = self.run_query(begin_date=self.current_job['begin_date'],
                                         end_date=self.current_job['end_date'],
                                         q='"' + self.current_job['place_name'] + '"',
                                         fq={'glocations': 'New York City'})

                if results is None:
                    raise NoResults

            except NoResults:
                LOGGER.debug("Returned null result set.")
            except InvalidAPIKey as e:

                msg = e.args[0]
                key = e.args[1]

                LOGGER.critical("Invalid API Key: {} - {}".format(msg, key))
                self.KEYRING.updateStatus(key, False)
                LOGGER.info("Current job: {}".format(self.current_job['place_name']))

                self.return_failed_job()

                # return_failed_job(self.redis_conn,
                #                   place_id=job['place_id'],
                #                   place_name=job['place_name'],
                #                   begin_date=job['begin_date'],
                #                   end_date=job['end_date'])

            except AllLimitsReached:
                LOGGER.warning("All API keys have reached their limits.")
                LOGGER.info("Current job: {}".format(self.current_job['place_name']))

                self.return_failed_job()

                break

            except APIError as e:
                LOGGER.error(e.args[0])
                self.return_failed_job()

            except json.JSONDecodeError:
                LOGGER.error("Error decoding response.")
                LOGGER.info("Current job: {}".format(self.current_job['place_name']))

                self.return_failed_job()

            else:
                # filter out empty results
                LOGGER.debug("Length of results before filtering out nones: {}".format(len(results)))
                results = list(filter(lambda x: x is not None, results))
                LOGGER.debug("Length of results after filtering out nones: {}".format(len(results)))

                if len(results) > 0:
                    all_results.append(dict(place_id=self.current_job['place_id'], query_results=results))

            finally:

                LOGGER.debug("Remaining: {}".format(rem_jobs))

                if rem_jobs == 0:
                    LOGGER.debug("Queue empty.")

        LOGGER.debug("Length of all_results before return: {}".format(len(all_results)))
        return all_results

    def return_failed_job(self):

        payload = json.dumps(self.current_job)

        try:
            self.redis_conn.lpush('queue', payload)
            LOGGER.info("Job failed, pushed to redis")
        except redis.RedisError as e:
            LOGGER.critical(e)


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
    dt = datetime.timedelta(days=1)
    yesterday = today - dt

    return _datestr(today), _datestr(yesterday)


def queue_jobs(conn, place_list, begin_date, end_date):

        try:
            pipe = conn.pipeline()
            pipe.multi()

            for p in place_list:

                job = {'place_id': p[0],
                       'place_name': p[1],
                       'begin_date': begin_date,
                       'end_date': end_date}

                payload = json.dumps(job)
                pipe.lpush('queue', payload)

            pipe.execute()

        except redis.RedisError as e:
            LOGGER.critical(e)


# def return_failed_job(conn, place_name, place_id, begin_date, end_date):
#
#     job = {'place_id': place_id,
#            'place_name': place_name,
#            'begin_date': begin_date,
#            'end_date': end_date}
#
#     payload = json.dumps(job)
#     try:
#         conn.lpush('queue', payload)
#     except redis.RedisError as e:
#         LOGGER.critical(e)


def execute_insertions_nyt(conn, data, feed_id, place_id):
    # connection, test_data, feed_id (for NYT API), place_id

    article_dict = make_article_tuple(data=data, feed_id=feed_id, as_dict=True)
    q_article = generate_article_query(list(article_dict.keys()))

    results = execute_query(conn, q_article, data=article_dict, return_values=True)
    article_id = results[0][1]

    tag_dict = make_place_tag_tuple(article_id=article_id, place_id=place_id, as_dict=True)
    #q_tag = generate_tag_query(list(tag_dict.keys()))
    q_tag = generate_place_mentions_query(list(tag_dict.keys()))

    execute_query(conn, q_tag, data=tag_dict, return_values=False)

    keyword_dicts = make_keyword_tuples(data=data, article_id=article_id, as_dict=True)
    if len(keyword_dicts) > 0:
        q_keyword = generate_keyword_query(list(keyword_dicts[0].keys()))
        for k in keyword_dicts:
            execute_query(conn, q_keyword, data=k, return_values=False)


def remove_duplicates(alist):

    de_duped = list()

    for item in alist:
        if item not in de_duped:
            de_duped.append(item)

    return de_duped


def insert_results_to_database(conn, all_results, feed_id):

    LOGGER.debug("Length of all_results: {}".format(len(all_results)))

    flattened_results = list()
    for place_results in all_results:
        place_id = place_results['place_id']
        for query_result in place_results['query_results']:
            flattened_results.append((place_id, query_result))

    LOGGER.debug("Length of flattened_results before removing duplicates {}".format(len(flattened_results)))
    flattened_results = remove_duplicates(flattened_results)
    LOGGER.debug("Length of flattened_results after removing duplicates {}".format(len(flattened_results)))

    for result in flattened_results:
        place_id = result[0]
        query_result = result[1]
        execute_insertions_nyt(conn, query_result, feed_id, place_id)


    # for place_results in all_results:
    #     place_id = place_results['place_id']
    #     for query_result in place_results['query_results']:
    #         execute_insertions_nyt(conn, query_result, feed_id, place_id)

# TODO: remove limit in prod
def get_places(conn, market_id):

    #QUERY = "SELECT place_id, place_name FROM places WHERE market_id = {}".format(market_id)
    QUERY = '''
    SELECT place_id, place_name 
    FROM media_markets INNER JOIN places ON media_markets.id = places.market_id 
    INNER JOIN place_aliases ON places.id = place_aliases.place_id WHERE market_id = {} LIMIT 5;
    '''.format(market_id)

    with conn.cursor() as curs:
        curs.execute(QUERY)
        results = curs.fetchall()

    return results


def clinton_purge(conn, feed_id):

    QUERY = '''
    CREATE TEMP VIEW clinton_purge AS (SELECT DISTINCT(articles.id) FROM articles 
	    INNER JOIN place_mentions ON articles.id = place_mentions.article_id
	    INNER JOIN place_aliases ON place_aliases.place_id = place_mentions.place_id
	    INNER JOIN keywords ON articles.id = keywords.article_id
        WHERE articles.feed_id={feed_id} 
	    AND place_aliases.place_id IN (SELECT place_id FROM place_aliases WHERE place_name = 'Chelsea' OR place_name = 'Clinton')
	    AND (keyword = 'Clinton, Hillary Rodham' OR keyword = 'Clinton, Bill' OR keyword = 'Clinton, Chelsea')
	    AND tag = 'persons');
	
    DELETE FROM keywords WHERE keywords.article_id IN (SELECT id FROM clinton_purge);
    DELETE FROM place_mentions WHERE place_mentions.article_id IN (SELECT id FROM clinton_purge);
    DELETE FROM articles WHERE articles.id IN (SELECT id FROM clinton_purge);

    DROP VIEW clinton_purge;
    '''.format(feed_id=feed_id)

    cursor = conn.cursor()

    try:
        cursor.execute(QUERY)
        LOGGER.info("Clintons purged.")
    except psycopg2.Error:
        LOGGER.error("Error in clinton purge.")
    finally:
        cursor.close()

    # with conn.cursor() as curs:
    #     LOGGER.info("Running Clinton purge.")
    #     curs.execute(QUERY)


def real_estate_purge(conn):
    QUERY = '''
    CREATE TEMP VIEW real_estate_purge AS (SELECT DISTINCT(keywords.article_id) FROM
        keywords WHERE keywords.keyword LIKE '%Real Estate%');
    
    DELETE FROM keywords WHERE keywords.article_id IN (SELECT article_id FROM real_estate_purge);
    DELETE FROM place_mentions WHERE place_mentions.article_id IN (SELECT article_id FROM real_estate_purge);
    DELETE FROM articles WHERE articles.id IN (SELECT article_id FROM real_estate_purge);
    
    DROP VIEW real_estate_purge;
    '''

    cursor = conn.cursor()

    try:
        cursor.execute(QUERY)
        LOGGER.info("Real estate purged.")
    except psycopg2.Error:
        LOGGER.exception("Real estate purge error.")
    finally:
        cursor.close()

    # with conn.cursor() as curs:
    #     LOGGER.info("Running Clinton purge.")
    #     curs.execute(QUERY)