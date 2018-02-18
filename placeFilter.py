import re
from SearchGraph import disambiguation_data
from SearchGraph import SearchGraph

# the class placeFilter creates a filter for a set of search graphs and single-expression names
# constructs a SearchGraph for each disambiguation_data object after converting dicts to disambiguation_data.
# Strings that are to be filtered and passed through the SearchGraphs and are checked against the single-expression names and 
# all matches are returned in a list

#### process place names ####

class placeFilter:
    
    filters = list()
    
    def __init__(self, filter_list):
         
        for i, j in enumerate(filter_list):
            if isinstance(j, dict):
                filter_list[i] = disambiguation_data(j)
        
        
        for i, p in enumerate(filter_list):
            if isinstance(p, disambiguation_data) == True:
                G = SearchGraph(p)
                G.prune_tree()
                filter_list[i] = G
                #filter_list[i].prune_tree()
                # need to run pruning operation
                
            elif isinstance(p, str) == True:
                filter_list[i] = p     
            else:
                raise ValueError("placeFilter must take either a string or disambiguation_data object.")

        self.filters = filter_list


    def checkFilters(self, string):
        matches = list()
        for p in self.filters:
            if isinstance(p, SearchGraph):
                p.count_matches(string)
                matches.extend(p.compute_actual())
            else:
                if re.search(p, string) != None:
                    #temp = re.findall(p, string)
                    matches.append(p)
        
        return matches