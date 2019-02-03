import logging
import redis
import psycopg2
from nyt_scraper.etl_utils import NYTScraper, generate_dates, queue_jobs, get_places
from nyt_scraper.etl_utils import insert_results_to_database

LOGGER = logging.getLogger('etl.execute_nyt_scraper')

def execute(api_keys, market_id, feed_id, pg_config, redis_config, begin_date=None, end_date=None):

    LOGGER.info("Starting NYT scraping cycle.")

    if begin_date is None or end_date is None:
        end_date, begin_date = generate_dates()

    pg_conn = psycopg2.connect(**pg_config)

    redis_conn = redis.Redis(**redis_config)

    place_list = get_places(pg_conn, market_id)
    scraper = NYTScraper(api_keys, conn=redis_conn)

    queue_jobs(redis_conn, place_list, begin_date=begin_date, end_date=end_date)
    results = scraper.execute_api_search()
    insert_results_to_database(pg_conn, results, feed_id)

    pg_conn.close()