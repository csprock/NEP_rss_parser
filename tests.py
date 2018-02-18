import re
from placeFilter import placeFilter
from SearchGraph import *
################################ demonstration of SearchGraph ################################
# initialize SearchGraph data structure
data_struct = {'root':'Portland', 
               'children': ['South Portland', 'West Portland', 'Portland Heights', 'South Portland Heights', 'South Portland Heights Park', 'West Portland Heights', 'South Portland Heights Grove'],
               'relations': [('Portland', 'South Portland'),
                         ('Portland', 'West Portland'),
                         ('Portland','Portland Heights'),
                         ('West Portland', 'West Portland Heights'),
                         ('Portland Heights','West Portland Heights'),
                         ('Portland Heights','South Portland Heights'),
                         ('South Portland','South Portland Heights'),
                         ('South Portland Heights','South Portland Heights Park'),
                         ('South Portland Heights', 'South Portland Heights Grove')]}


# create disambiguation_data object
data = disambiguation_data(data_struct)
# initialize search graph
G = SearchGraph(data)

string = '''
        Welcome to West Portland Heights! A suburb of South Portland, 
        which is next to South Portland Heights but not to be confused with
        South Portland Heights Grove, which are all part of Portland.
        '''





# STAGE 1: count total matches in string
G.count_matches(string)
G.print_matches()

# STAGE 2: compute actual matches in string
true_matches = G.compute_actual()
G.print_actual()


########################## demonstration of placeFilter #######################

data_struct1 = {'root':'Crown Heights',
               'children' : ['Crown Heights Plaza'],
               'relations': [('Crown Heights', 'Crown Heights Plaza')]}
        


singleton = 'New Haven'

places = [disambiguation_data(data_struct), disambiguation_data(data_struct1), singleton]


string = '''
        Welcome to West Portland Heights! A suburb of South Portland, 
        which is next to South Portland Heights but not to be confused with
        South Portland Heights Grove, which are all part of Portland. The Crown Heights Plaza area is 
        next to the New Haven school.
        '''
        
name_filter = placeFilter(places)
name_filter.checkFilters(string)


        
        







    
    




