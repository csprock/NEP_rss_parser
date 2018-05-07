import psycopg2

def connect_to_database(conn_info, success_message = True):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (conn_info['host'], conn_info['dbname'], conn_info['username'], conn_info['password'])
    try:
        conn = psycopg2.connect(conn_string)
        if success_message is True:
            print("Connected to database %s." % (conn_info['dbname']))

        return conn
    except:
        print('Error! Failure to connect to database %s' % (conn_info['dbname']))


def execute_query(conn_obj, query, data = None, return_values = False):
    
    with conn_obj as conn:
        with conn.cursor() as curs:
            if data is not None:
                curs.execute(query, data)
                if return_values:
                    to_return = curs.fetchall()
            else:
                curs.execute(query)
                if return_values:
                    to_return = curs.fetchall()

    if return_values:
        return to_return