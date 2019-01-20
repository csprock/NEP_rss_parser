from queue import Queue
from threading import Thread
from rssScraper.parser.parsing_utils import parse_feed, make_place_filter, execute_insertions

FEED_INFO_QUERY = '''
    SELECT market_id, feed_id, url
    FROM publishers INNER JOIN feeds
    ON publishers.pub_id = feeds.pub_id
    WHERE url IS NOT NULL;
'''


class RSSWorker(Thread):

    def __init__(self, conn, queue_in, queue_out):
        Thread.__init_added_(self)
        self.conn = conn
        self.queue_in = queue_in
        self.queue_out = queue_out

    def run(self):

        while True:

            market_id, feed_id, url = self.queue_in.get()
            G = make_place_filter(self.conn, market_id)
            results = parse_feed(url, feed_id, G)

            if results is not None:
                [self.queue_out.put(r) for r in results]

            self.queue_in.task_done()


def execute_rss_parser(conn):

    # get feeds and market ids
    with conn.cursor() as curs:
        curs.execute(FEED_INFO_QUERY)
        feed_info = curs.fetchall()

    # create queues
    feed_queue = Queue()
    db_queue = Queue()

    # start workers
    for worker in range(len(feed_info)):
        worker = RSSWorker(conn, feed_queue, db_queue)
        worker.daemon = True
        worker.start()

    # add feeds to queue
    for f in feed_info:
        feed_queue.put(f)

    feed_queue.join()

    # insert results into database
    while not db_queue.empty():
        item = db_queue.get()
        execute_insertions(item, conn)
        db_queue.task_done()

