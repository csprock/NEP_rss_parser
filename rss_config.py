import psycopg2


CONN_INFO = {'dbname':'rss_feed_5', 'username':'postgres','password':'redalert'}

def connectToDatabase(conn_info, success_message = True):
    conn_string = "host='localhost' dbname='%s' user='%s' password='%s'" % (conn_info['dbname'], conn_info['username'], conn_info['password'])
    try:
        conn = psycopg2.connect(conn_string)
        if success_message is True:
            print("Connected to database %s." % (conn_info['dbname']))
            
        return conn
    except:
        print('Error! Failure to connect to database %s' % (conn_info['dbname']))