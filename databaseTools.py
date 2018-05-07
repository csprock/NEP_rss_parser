import psycopg2
import pandas as pd
from psycopg2 import sql

# this script contains functions for:
    # connecting to database
    # executing SELECT query
    # replacing capitalized duplicates
    # deleting records associated with an article ID
    # replacing tag names

#CONN_INFO = {'dbname':'',
#             'password':'',
#             'username':'',
#             'host':''}
#
#conn = connectToDatabase(CONN_INFO)
#
#tbl_info = ['hello', 'world']
#q = sql.SQL("UPDATE {tbl} SET {fld} = (%s) WHERE {fld} = (%s);").format(tbl = sql.Identifier(tbl_info[0]), fld = sql.Identifier(tbl_info[1])).as_string(conn)

###################################################
########## query  database     ####################
###################################################
# functions:
    # connectToDatabase()
    # executeSQL_select()

# connection_info = {dbname, username, password}


#connect to PostgreSQL database, returns connection object if successful, otherwise prints error
def connectToDatabase(conn_info, success_message = True):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (conn_info['host'], conn_info['dbname'], conn_info['username'], conn_info['password'])
    try:
        conn = psycopg2.connect(conn_string)
        if success_message is True:
            print("Connected to database %s." % (conn_info['dbname']))

        return conn
    except:
        print('Error! Failure to connect to database %s' % (conn_info['dbname']))


def executeQuery(conn_obj, query, data = None, return_values = False):
    
    
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





# compact function for SQL SELECT query
def executeSQL_select(query, tupl, conn_info, success_message = False, column_names = None):
    conn = connectToDatabase(conn_info, success_message = success_message)
    cur = conn.cursor()
    if tupl is not None:
        cur.execute(query, tupl)
    else:
        cur.execute(query)
    results = cur.fetchall()
    cur.close
    conn.close
    if column_names is not None:
        results = pd.DataFrame(results, columns = column_names)
    else:
        results = pd.DataFrame(results)

    return results






# executeSQL_select("SELECT COUNT(*) FROM tags WHERE keyword = (%s);", ("Missing Persons",), "nyc_neighborhood_articles", "redalert", "postgres", success_message = True)



##############################################
#### replacing capitalized duplicate tags #### v 1.0
##############################################

# some keyword tags have capitalized duplicates such as 'Housing' and 'HOUSING'
# since SQL is case-sensitive, these must be standardized
# these functions replace capitalized duplicate tags with specified replacement

# to use: enter a tag such as 'Housing', the functions scans through database looking for 'HOUSING' and replaces with 'Housing'
# set global variables to be used by database connectors


#conn_info = {'dbname':'nyc_neighborhood_articles', 'username':'postgres','password':'redalert'}

#def is_capitalized(tag):
#    if tag == tag.upper():
#        return True
#    else:
#        return False
#
#
#def replace_capitalized_tags(tag, conn_info, tbl_info):
#
#
#    if is_capitalized(tag) == False:
#
#        conn = connectToDatabase(conn_info, success_message = False)
#        cursor = conn.cursor()
#        try:
#            q = sql.SQL("UPDATE {tbl} SET {fld} = (%s) WHERE {fld} = (%s);").format(tbl = sql.Identifier(tbl_info[0]), fld = sql.Identifier(tbl_info[1])).as_string(conn)
#            cursor.execute(q, (tag, tag.upper()))
#            #cursor.execute("UPDATE tags SET keyword = (%s) WHERE keyword =(%s);", (tag, tag.upper()))
#            conn.commit()
#        except psycopg2.IntegrityError as err:
#            cursor.close()
#            conn.close()
#            ID = err.diag.message_detail.split('(')[2].split(',')[0]
#
#            try:
#                conn = connectToDatabase(conn_info, success_message = False)
#                cursor = conn.cursor()
#                q2 = sql.SQL("DELETE FROM {tbl} WHERE {fld} = (%s) AND id = (%s);").format(tbl = sql.Identifier(tbl_info[0]), fld = sql.Identifier(tbl_info[1])).as_string(conn)
#                cursor.execute(q2, (tag.upper(), ID))
#                conn.commit()
#            except psycopg2.Error as err:
#                print(err)
#
#        except psycopg2.Error as err:
#            print(err)
#
#        cursor.close()
#        conn.close()
#        print("Replacing %s complete." % tag)
#    else:
#        print("Already Capitalized.")
#
#
#
#def run_replace(tag, conn_info, tbl_info):
#
#    indicator = is_capitalized(tag)
#
#    if indicator == False:
#
#        # get number of capitalized tags
#
#        counts = executeSQL_select("SELECT COUNT(*) FROM tags WHERE keyword = (%s);", (tag.upper(), ), conn_info)
#        counts = int(counts.values[0][0])
#
##        conn = connectToDatabase(db_name, pwd, usr, success_message = False)
##        cursor = conn.cursor()
##        cursor.execute("SELECT COUNT(*) FROM tags WHERE keyword = (%s);", (tag.upper(), ))
##        counts = cursor.fetchall()
##        counts = int(counts[0][0])
##        cursor.close()
##        conn.close()
#
#        # iteratively replace capitalized duplicates until none remain
#        while counts > 0:
#
#            counts = executeSQL_select("SELECT COUNT(*) FROM tags WHERE keyword = (%s);", (tag.upper(), ), conn_info)
#            counts = int(counts.values[0][0])
#
#            replace_capitalized_tags(tag, conn_info, tbl_info)
#
#        print("Replace '%s' Complete." % tag)
#
#    else:
#        print('Capitalized entry. Skipping')
#
#
##### usage:
#
##keyword_list = executeSQL_select("SELECT DISTINCT(keyword) FROM tags;", db_name, psswrd, usr)
##keyword_list = [kwrd[0] for kwrd in keyword_list]
##
##for kwrd in keyword_list:
##    run_replace(kwrd)
#
##############################################
############ replacing tags ################## v 1.1
##############################################
#
## some tags should be merged, for instance "Murders, Attempted Murders and Homicides"
## and "Murders and Attempted Murders" should be a single tag
#
## this function executes a find-and-replace operation on keyword tags
#
## replace_pair = {'original','replacement'}
#
#def replace_tags(replace_pair, conn_info):
#
#    conn = connectToDatabase(conn_info, success_message = False)
#    cursor = conn.cursor()
#    try:
#        cursor.execute("UPDATE tags SET keyword = (%s) WHERE keyword =(%s);", (replace_pair['replacement'], replace_pair['original']))
#        conn.commit()
#    except psycopg2.IntegrityError as err:
#        cursor.close()
#        conn.close()
#        ID = err.diag.message_detail.split('(')[2].split(',')[0]
#
#        try:
#            conn = connectToDatabase(conn_info, success_message = False)
#            cursor = conn.cursor()
#            cursor.execute("DELETE FROM tags WHERE keyword = (%s) AND id = (%s);", (replace_pair['original'], ID))
#            conn.commit()
#        except psycopg2.Error as err:
#            print(err)
#
#    except psycopg2.Error as err:
#        print(err)
#
#    cursor.close()
#    conn.close()
#
## this function iterates replace_tags() until all records have been replaced
#def run_replace_tags(replace_pair, conn_info):
#
#
#
#    counts = executeSQL_select("SELECT COUNT(*) FROM tags WHERE keyword = (%s);", (replace_pair['original'], ), conn_info)
#    counts = counts.values[0][0]
#
##    conn = connectToDatabase(db_name, psswrd, usr, success_message = False)
##    cursor = conn.cursor()
##    cursor.execute("SELECT COUNT(*) FROM tags WHERE keyword = (%s);", (tag, ))
##    counts = cursor.fetchall()
##    counts = int(counts[0][0])
##    cursor.close()
##    conn.close()
#
#    while counts > 0:
#
#        counts = executeSQL_select("SELECT COUNT(*) FROM tags WHERE keyword = (%s);", (replace_pair['original'], ), conn_info)
#        counts = counts.values[0][0]
#
#        replace_tags(replace_pair, conn_info)
#
#    print('Replace "%s" Complete.' % tag)
#
#
##### usage:
#
##run_replace_tags("BLACKS (IN US)", "Blacks")
#
#
######################################################
##### deleting records associated with an article #### v 1.1
######################################################
#
## the same article can be associated with multiple search queries or a single search query
## this function does the following:
#    # if article ID associated with multiple query, only query deleted if remove_all is False (default)
#    # removes all records associated with query if remove_all is True or
#    # removes all recoreds associated with query if article associated with single query
#
#
#
## search_term:
## ID: article ID
#def delete_query(search_term, ID, remove_all = False):
#
#    global db_name, psswrd, usr
#
#
#    results = executeSQL_query("SELECT * FROM query WHERE id = (%s);", (ID,), db_name, psswrd, usr, success_message = False)
#
#
#    # if there are multiple queries associated to the same article ID, delete entry only from query table
#    if len(results) > 1:
#
#        conn = connectToDatabase(db_name, psswrd, usr, success_message = False)
#        cur = conn.cursor()
#        cur.execute("DELETE FROM query WHERE id = (%s) AND query = (%s);", (ID, search_term))
#        conn.commit()
#        cur.close()
#        conn.close()
#    # if only one query assigned to an article ID, delete all article data from all tables
#    elif len(results) == 1 or remove_all == True:
#
#        conn = connectToDatabase(db_name, psswrd, usr, success_message = False)
#        cur = conn.cursor()
#        cur.execute(
#                '''
#                DELETE FROM query WHERE id = (%s);
#                DELETE FROM tags WHERE id = (%s);
#                DELETE FROM article WHERE id = (%s);
#                ''',
#                (ID,ID,ID))
#        conn.commit()
#        cur.close()
#        conn.close()
#    else:
#        raise Exception
