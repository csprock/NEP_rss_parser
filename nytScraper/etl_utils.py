
from resultsParser import processResults
import datetime
from psycopg2 import sql
import psycopg2

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




#
#keyring = KEYRING(API_KEYS)
#
#keyring.checkKeys()
#keyring.updateStatus('d7117d6c63404420b03ee92aa4ec9806', False)







def executeQuery(api_obj, **kwargs):

    """
    Is a wrapper function for the articleAPI.search() function that parses return messages
    and errors. This function takes the articleAPI object and the arguments to be passed to the object. 
    The arguments are passed to the articleAPI.search() function and the results of the function parsed. 
    A dictionary containing the information about status messages and the data if the query execution
    was successful.
    
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
        returns True when there are results to parse. Returns false of any of the following are true:
    output_data: 
        results['response']['docs'] or NoneType depending on results of query
    api_limit: bool
        True if API limit rate exceeded

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
                print("No results found.")
                   
            else:
                output_status = True
                #output_data = results['response']['docs']
                output_data = processResults(results)
        else:
            output_status = False
            print("Error")


    except KeyError:      
        output_status = False
        
        # checks for message in the return packet
        if results['message'] == 'API rate limit exceeded':
            print(results['message'])
            api_limit = True
        else:
            print(results['message'])
            
    
    return {'status':output_status, 'api_status': api_limit, 'data':output_data, 'hits': hits}



def connectToDatabase(conn_info, success_message = True):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (conn_info['host'], conn_info['dbname'], conn_info['username'], conn_info['password'])
    try:
        conn = psycopg2.connect(conn_string)
        if success_message is True:
            print("Connected to database %s." % (conn_info['dbname']))
            
        return conn
    except:
        print('Error! Failure to connect to database %s' % (conn_info['dbname']))



###############################################################################
# the following functions are specific to the database schema and will have
# to be updated if the database is updated


def makeArticleTuple(feed_id, data, as_dict = False):
    
    date_parts = list(map(int, data['date'].split("-")))
    
    
    if as_dict:
        output = dict()
        output['feed_id'] = feed_id
        output['headline'] = data['headline']
        output['date'] = datetime.date(date_parts[0], date_parts[1], date_parts[2])
        output['summary'] = data['snippet']
        output['byline'] = None
        output['wordcount'] = data['word_count']
        output['page_number'] = data['page']
        output['url'] = data['url']
    else:
        output = (feed_id,  
                    data['headline'],
                    datetime.date(date_parts[0],date_parts[1],date_parts[2]),
                    data['snippet'],
                    None,
                    data['word_count'],
                    data['page'],
                    data['url'])
      
    return output



def makePlaceMentionsTuple(article_id, place_id, as_dict = False):
    
    if as_dict:
        output = dict()
        output['article_id'] = article_id
        output['place_id'] = place_id
    else:
        output = (article_id, place_id)
        
    return output



class databaseInserter:
    
    

    def __init__(self, conn_info):
        
        self.CONN = connectToDatabase(conn_info)
        
        self.base_query_1 = '''
        WITH input_rows({}) AS (VALUES ({})), ins AS (INSERT INTO {}({}) 
        SELECT * FROM input_rows ON CONFLICT (url) DO NOTHING RETURNING id) 
        SELECT 'inserted' AS source, id FROM ins UNION ALL 
        (SELECT 'selected' AS source, {}.id FROM input_rows JOIN {} USING(url))
        '''
        
        self.base_query_2 = "INSERT INTO {}({}) VALUES ({})"
        
        self.duplicates = []
        
        
        
    def _generateSQL_1(self, values):
    
        f_dict = {k:v for k, v in values.items() if v != None}
        
        field_names = f_dict.keys()
        
        # create SQL variables
        table_name = sql.Identifier('articles')
        fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
        placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))
        
        # feed variables to psycopg2's sql statement formatter
        q = sql.SQL(self.base_query_1).format(fields, placeholders, table_name, fields, table_name, table_name)
        return q
    

    def _generateSQL_2(self, values):
    
        field_names = values.keys()
        
        # create SQL variables
        table_name = sql.Identifier('place_mentions')
        fields = sql.SQL(', ').join(map(sql.Identifier, field_names))
        placeholders = sql.SQL(', ').join(map(sql.Placeholder,field_names))
        
        # feed variables to psycopg2's sql statement formatter
        q = sql.SQL(self.base_query_2).format(table_name, fields, placeholders)
        return q
    
    
        
    def executeInsertion(self, feed_id, place_id, data):
        
        valueTuple1 = makeArticleTuple(feed_id, data, as_dict = True)
        q1 = self._generateSQL_1(valueTuple1)
        
        with self.CONN as conn:
            with conn.cursor() as curs:
                curs.execute(q1, valueTuple1)
                returned_id = curs.fetchall()
                
        
        if returned_id[0][0] == 'selected':
            print("Duplicate found at article_id: %s" % str(returned_id[0][1]))
            self.duplicates.append((returned_id[0][1], place_id))
            
            
        
        valueTuple2 = makePlaceMentionsTuple(returned_id[0][1], place_id, as_dict = True)
        q2 = self._generateSQL_2(valueTuple2)
        
        with self.CONN as conn:
            with conn.cursor() as curs:
                curs.execute(q2, valueTuple2)
                
        







        