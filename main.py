import argparse
import os
import json
import psycopg2
from pytz import timezone

import logging
import logging.config

with open('logging.json', 'r') as f:
    logging_config = json.load(f)

logging.config.dictConfig(logging_config)
LOGGER = logging.getLogger('etl')

from rssScraper.parser.parser import execute_rss_parser
from nytScraper.execute_nyt_scraper import execute as nyt_execute

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

PG_HOST = os.environ['PG_HOST']
PG_PASSWORD = os.environ['PG_PASSWORD']
PG_USER = os.environ['PG_USER']
PG_DB = os.environ['PG_DB']
PG_PORT = os.environ['PG_PORT']

REDIS_HOST = os.environ.get('REDIS_HOST', None)
REDIS_DB_NYT = os.environ['REDIS_DB_NYT']
REDIS_DB_SCHEDULER = os.environ['REDIS_DB_SCHEDULER']
REDIS_PORT = os.environ['REDIS_PORT']

API_KEYS = os.environ['API_KEYS'].split(',')
MARKET_ID = int(os.environ['NYT_MARKET_ID'])
FEED_ID = int(os.environ['NYT_FEED_ID'])

PG_CONFIG = {
    'user': PG_USER,
    'dbname': PG_DB,
    'port': PG_PORT,
    'host': PG_HOST,
    'password': PG_PASSWORD
}

REDIS_CONFIG = {
    'port': REDIS_PORT,
    'db': REDIS_DB_NYT,
    'host': REDIS_HOST
}

jobstores = {
    'default': RedisJobStore(db=REDIS_DB_SCHEDULER)
}
executors = {
    'default': ThreadPoolExecutor(max_workers=1)
}
job_defaults = {
    'max_instances': 1
}

scheduler = BlockingScheduler(jobstores=jobstores,
                                executors=executors,
                                job_defaults=job_defaults)


rss_trigger = IntervalTrigger(hours=4)
# nyt_test_trigger = IntervalTrigger(minutes=1)

nyt_trigger = CronTrigger(month='*',
                          day='*',
                          week='*',
                          day_of_week='*',
                          hour='0',
                          minute='0',
                          second='0',
                          timezone=timezone('US/Eastern'))

scheduler.add_job(execute_rss_parser,
                  id='rss',
                  trigger=rss_trigger,
                  max_instances=1,
                  executor='default',
                  kwargs={'pg_config': PG_CONFIG})

# nyt_test_trigger = CronTrigger(month='*',
#                           day='*',
#                           week='*',
#                           day_of_week='*',
#                           hour='20',
#                           minute='18',
#                           second='0',
#                           timezone=timezone('US/Central'))

scheduler.add_job(nyt_execute,
                  trigger=nyt_trigger,
                  id='nyt',
                  executor='default',
                  max_instances=1,
                  kwargs={'pg_config': PG_CONFIG,
                          'redis_config': REDIS_CONFIG,
                          'api_keys': API_KEYS,
                          'market_id': MARKET_ID,
                          'feed_id': FEED_ID})


if __name__ == '__main__':
    LOGGER.info("Starting scheduler.")
    scheduler.start()
