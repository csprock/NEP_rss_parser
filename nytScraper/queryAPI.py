from articleAPI import articleAPI
import time
from etl_utils import KEYRING, executeQuery



class nytScraper:
    
    def __init__(self, key):
        self.KEYRING = KEYRING(key)

    def runQuery(self, page_range, **kwargs):
    
        if isinstance(page_range, list):
            current_page, stop_page = page_range[0], page_range[1]
        elif page_range == 'all':
            current_page, stop_page = 0, 200
            
        # initialize variables
        #keyring = self.KEYRING(keylist)                 # initialize KEYRING object
        current_key = self.KEYRING.nextKey()             # set current API key to use
        
        

        api_obj = articleAPI(current_key)                # initialize articleAPI object using current_key
        results_list = list()                            # initialize list where results of queries will be stored
        
        
        # Check the number of hits and the number of pages needed to download all of them. 
        # If number of pages exceeds maximum allowed by the API (200), returns exception. 
        #kwargs['page']  = current_page
        results = executeQuery(api_obj, page = current_page, **kwargs)
        hits = results['hits']
        
        if hits == 0 or hits == None:
            return None
        
        
        hits_pages = hits // 10
    
        if hits_pages > 200:
            raise ValueError("The number of pages will exceed 200! Number of hits is " + str(hits))
        else:
            print("Number of results pages: " + str(hits_pages) + " Number of hits: " + str(hits))
        
        
        while True: # loop runs until stop condition breaks it
            
            # patch to fix expanding string bug
            for k in kwargs.keys():
                if isinstance(kwargs[k], dict):
                    for u in kwargs[k].keys():
                        if isinstance(kwargs[k][u], str):
                            kwargs[k][u] = kwargs[k][u].replace('"', '').strip()
             
                
            time.sleep(1)
            
            results = executeQuery(api_obj, page = current_page, **kwargs)
            
            if results['status'] == True:
                
                results_list.extend(results['data'])
                print("Status: OK. Current page: " + str(current_page))
                current_page += 1
    
            else:
                # check API status, if API limit reached set status of current key to False and update current key
                # If all keys have reached their limits, print message and break.
                
                if results['api_status']:
                    self.KEYRING.updateStatus(current_key, False)
                    
                    # if there is another usable key, set current_key to this key otherwise breaks main loop.
                    if self.KEYRING.status():
                        current_key = self.KEYRING.nextKey()
                        api_obj = articleAPI(current_key)
                        
                    else:
                        print("All API keys have reached their limits.")
                        break
                    
    
            if current_page > min([hits_pages, stop_page]):
                break
            
        return results_list
    
    
    
    
    
    
    
    
    
   
    
    




#    
#kw = dict(q = 'harlem', fq = {'glocations':'"New York"', 'c':0}, page = 0)
#
#for u in kw.keys():
#    
#    if isinstance(kw[u], dict):
#        
#        for v in kw[u]:
#            if isinstance(kw[u][v], str):
#                kw[u][v] = kw[u][v].replace('"','').strip()
#        
#        #kw[u] = kw[u].replace('"','').strip()


#def getResults(page_range, keylist, **kwargs):
#
#    
#    
#    assert isinstance(page_range, list)
#    
#    # initialize variables
#    keyring = KEYRING(keylist)              # initialize KEYRING object
#    current_key = keyring.nextKey()         # set current API key to use
#    current_page, stop_page = page_range[0], page_range[1]        
#    api_obj = articleAPI(current_key)       # initialize articleAPI object using current_key
#    results_list = list()                   # initialize list where results of queries will be stored
#    
#    
#    # Check the number of hits and the number of pages needed to download all of them. 
#    # If number of pages exceeds maximum allowed by the API (200), returns exception. 
#    #kwargs['page']  = current_page
#    results = executeQuery(api_obj, page = current_page, **kwargs)
#    hits = results['hits']
#    hits_pages = hits // 10
#
#    if hits_pages > 200:
#        raise ValueError("The number of pages will exceed 200! Number of hits is " + str(hits))
#    else:
#        print("Number of results pages: " + str(hits_pages) + " Number of hits: " + str(hits))
#    
#    
#    while True:
#        # loop runs until stop condition breaks it
#        time.sleep(1)
#
#        # append current_page to kwargs to pass to executeQuery()
#        #kwargs['page'] = current_page
#        # Query API
#        
#        
#        
#        for k in kwargs.keys():
#            if isinstance(kwargs[k], dict):
#                for u in kwargs[k].keys():
#                    if isinstance(kwargs[k][u], str):
#                        kwargs[k][u] = kwargs[k][u].replace('"', '').strip()
#            
#            
#                    results = executeQuery(api_obj, page = current_page, **kwargs)
#        
#        if results['status'] == True:
#            
#            results_list.extend(results['data'])
#            print("Status: OK. Current page: " + str(current_page))
#            current_page += 1
#
#        else:
#            # check API status, if API limit reached set status of current key to False and update current key
#            # If all keys have reached their limits, print message and break.
#            
#            if results['api_status']:
#                keyring.updateStatus(current_key, False)
#                
#                # if there is another usable key, set current_key to this key otherwise breaks main loop.
#                if keyring.status():
#                    current_key = keyring.nextKey()
#                    api_obj = articleAPI(current_key)
#                    
#                else:
#                    print("All API keys have reached their limits.")
#                    break
#                
#
#        if current_page > min([hits_pages, stop_page]):
#            break
#        
#    return results_list, keyring
                
    
    
    
    
    







