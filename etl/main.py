import os
import json
from pytz import timezone
import redis
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--nyt_begin', type=str, default=None)
parser.add_argument('--nyt_end', type=str, default=None)

args = parser.parse_args()
# NYT_BEGIN = args.nyt_begin
# NYT_END = args.nyt_end

import logging.config

with open('logging.json', 'r') as f:
    logging_config = json.load(f)

logging.config.dictConfig(logging_config)
LOGGER = logging.getLogger('etl')
APSCHEDULER_LOGGER = logging.getLogger('apscheduler.scheduler')

from rss_scraper.parser.parser import execute_rss_parser as rss_execute
from nyt_scraper.execute_nyt_scraper import execute as nyt_execute
from nyt_scraper.etl_utils import generate_dates

_, nyt_begin = generate_dates()

NYT_BEGIN = args.nyt_begin if args.nyt_begin is not None else nyt_begin
NYT_END = args.nyt_begin if args.nyt_begin is not None else nyt_begin

LOGGER.info("NYT Start and end dates: {}, {}".format(NYT_BEGIN, NYT_END))


from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Postgres credentials
PG_HOST = os.environ['PGHOST']
PG_PASSWORD = os.environ['PGPASSWORD']
PG_USER = os.environ['PGUSER']
PG_DB = os.environ['PGDATABASE']
PG_PORT = os.environ['PGPORT']

# redis credentials
REDIS_HOST = os.environ.get('REDIS_HOST', None)
REDIS_DB_NYT = os.environ['REDIS_DB_NYT']
REDIS_DB_SCHEDULER = os.environ['REDIS_DB_SCHEDULER']
REDIS_PORT = os.environ['REDIS_PORT']

INIT_REDIS = os.environ['INIT_REDIS']

# API keys
API_KEYS = os.environ['API_KEYS'].split(',')
MARKET_ID = int(os.environ['NYT_MARKET_ID'])
FEED_ID = int(os.environ['NYT_FEED_ID'])

# NYT job config

NYT_DAY = os.environ.get('NYT_DAY')
NYT_MONTH = os.environ.get('NYT_MONTH')
NYT_WEEK = os.environ.get('NYT_WEEK')
NYT_DAY_OF_WEEK = os.environ.get('NYT_DAY_OF_WEEK')
NYT_HOUR = os.environ['NYT_HOUR']
NYT_MINUTE = os.environ['NYT_MINUTE']
NYT_SECOND = os.environ['NYT_SECOND']

# RSS job config

# RSS_DAY = os.environ.get('RSS_DAY')
# RSS_MONTH = os.environ.get('RSS_MONTH')
# RSS_WEEK = os.environ.get('RSS_WEEK')
# RSS_DAY_OF_WEEK = os.environ.get('RSS_DAY_OF_WEEK')
# RSS_HOUR = os.environ.get('RSS_HOUR')
# RSS_MINUTE = os.environ['RSS_MINUTE']
# RSS_SECOND = os.environ['RSS_SECOND']
#
# RSS_INTERVAL = os.environ['RSS_INTERVAL']

NYT_SCHEDULE_CONFIG = {
    'month': NYT_MONTH,
    'day': NYT_DAY,
    'week': NYT_WEEK,
    'day_of_week': NYT_DAY_OF_WEEK,
    'hour': NYT_HOUR,
    'minute': NYT_MINUTE,
    'second': NYT_SECOND,
    'timezone': timezone('US/Eastern')
}


# RSS_SCHEDULE_CONFIG = {
#     'month': RSS_MONTH,
#     'day': RSS_DAY,
#     'week': RSS_WEEK,
#     'day_of_week': RSS_DAY_OF_WEEK,
#     'hour': RSS_HOUR,
#     'minute': RSS_MINUTE,
#     'second': RSS_SECOND,
#     'timezone': timezone('US/Eastern')
# }


PG_CONFIG = {
    'user': PG_USER,
    'dbname': PG_DB,
    'port': PG_PORT,
    'host': PG_HOST,
    'password': PG_PASSWORD
}

REDIS_CONFIG_NYT = {
    'port': REDIS_PORT,
    'db': REDIS_DB_NYT,
    'host': REDIS_HOST
}

REDIS_CONFIG_SCHEDULER = {
    'port': REDIS_PORT,
    'db': REDIS_DB_SCHEDULER,
    'host': REDIS_HOST
}

if int(os.environ['INIT_REDIS']) == 1:

    redis_conn_apscheduler = redis.Redis(**REDIS_CONFIG_SCHEDULER)
    _ = redis_conn_apscheduler.delete('apscheduler.jobs')

    LOGGER.info("Previous jobstore overridden.")

    redis_conn_queue = redis.Redis(**REDIS_CONFIG_NYT)
    _ = redis_conn_queue.delete('queue')

    LOGGER.info("Previous queue overridden.")



jobstores = {
    'default': RedisJobStore(**REDIS_CONFIG_SCHEDULER)
}
executors = {
    'default': ThreadPoolExecutor(max_workers=2)
}
job_defaults = {
    'max_instances': 1
}

scheduler = BlockingScheduler(jobstores=jobstores,
                                executors=executors,
                                job_defaults=job_defaults,
                              logging=APSCHEDULER_LOGGER)

####### define triggers ######

#rss_interval_trigger = IntervalTrigger(hours=RSS_INTERVAL)

nyt_trigger = CronTrigger(**NYT_SCHEDULE_CONFIG)
#rss_trigger = CronTrigger(**RSS_SCHEDULE_CONFIG)


####### add jobs #######

# scheduler.add_job(rss_execute,
#                   id='rss',
#                   trigger=rss_trigger,
#                   max_instances=1,
#                   executor='default',
#                   kwargs={'pg_config': PG_CONFIG})



# scheduler.add_job(nyt_execute,
#                   trigger=nyt_trigger,
#                   id='nyt',
#                   executor='default',
#                   max_instances=1,
#                   kwargs={'pg_config': PG_CONFIG,
#                           'redis_config': REDIS_CONFIG_NYT,
#                           'api_keys': API_KEYS,
#                           'market_id': MARKET_ID,
#                           'feed_id': FEED_ID,
#                           'begin_date': NYT_BEGIN,
#                           'end_date': NYT_END})


KWARGS = {'pg_config': PG_CONFIG,
          'redis_config': REDIS_CONFIG_NYT,
          'api_keys': API_KEYS,
          'market_id': MARKET_ID,
          'feed_id': FEED_ID,
           'begin_date': NYT_BEGIN,
           'end_date': NYT_END}

if __name__ == '__main__':
    LOGGER.info("Starting scraper.")
    nyt_execute(**KWARGS)
    LOGGER.info("Finished.")
