import re

def nameType(place_list):
    """
    This function takes a list of places as strings and determines the string-substring relationships 
    between them. Strings represent places, so a substring represents a "parent" of a "child", e.g.
    "San Francisco" would be the parent of "South San Francisco". 
    
    Input
    -----
    place_list: list
        list of place names
        
    Returns
    -------
    roots: list
        list containing strings that are parents but not children
    children: list
        list containing strings that have parents
    singles: list
        list containing strings that are neither parents or children
        
    """
    place_list = list(set(place_list))
    
    place_list.sort(key = len)
    
    # initialize dictionary of indicators for each place name
    indicators = dict()
    for p in place_list: indicators[p] = {'is_parent':False, 'is_child':False}
    
    
    # Identify parents and children
    for i in range(len(place_list)):
        current = place_list.pop(0)
        for p in place_list:
            if re.search(current, p) != None:
                indicators[current]['is_parent'] = True
                indicators[p]['is_child'] = True
    
    
    
    roots, singles, children = [],[],[]
    
    #populate lists containing roots, children and singletons
    for p in indicators:
        if indicators[p]['is_child'] == False and indicators[p]['is_parent'] == True:    # root strings are parents but not children
            roots.append(p)
        elif indicators[p]['is_child'] == False and indicators[p]['is_parent'] == False: # singles are neither parents nor children 
            singles.append(p)
        else:
            children.append(p)                                                           # rest are children of some parent

    #roots.sort(key = len)
    #children.sort(key = len)
    #singles.sort(key = len)
    
    
    return roots, children, singles





def next_edge_set(place_name, place_list):
    """
    This function returns a list of tuples of the form (place_name, places place_name is contained as a substring).
    
    Input
    -----
    place_name: str
    place_list: list of str
    
    Returns
    ------
    edges: list of tuples
    
    """
    edges = list()
    for p in place_list:
        if re.search(place_name, p) != None: 
            edges.append((place_name, p))
            
    return edges


def makeEdgeSet(place_list):
    """
    Makes edge list for use with a Graph object. Edge list is a list of tuples of the form (substring, string). 
    Applies next_edge_set() function to a sorted version of place_list. 
    
    Input
    -----
    place_list: list of str
    
    Returns
    -------
    E: list of tuples
    
    """
    
    place_list.sort(key = len)
    E = list()

    for i in range(len(place_list) - 1):
        es = next_edge_set(place_list[i], place_list[(i+1):])
        E.extend(es)
        
    return E





def makeGraphData(place_list):
    """
    Takes a list of places are returns all the data needed to initialize a SearchGraph object. Function 
    requires placeType() and makeEdgeSet() functions. 
    
    Input
    -----
    place_list: list of str
    
    Returns
    -------
    R: list of root nodes
    E: edge set of SearchGraph
    V: vertex set of SearchGraph
    """
    
    R, C, S = nameType(place_list)
    E = makeEdgeSet(R+C)
    V = R + C + S
    R = R + S
    
    return R, V, E










      
## inputs root/parent name, list of child names
## outputs list of names belonging to the same family tree with the root/parent as first element
#def make_family_list(root, children):
#    
#    family_list, child_list = [root], []
#    
#    # match children with root
#    for c in children:
#        if re.search(root, c) != None: child_list.append(c)
#    
#    child_list.sort(key = len)
#    # extend family list with children
#    family_list.extend(child_list)
#    return family_list
#    
#
#
#
#def createFamilyStructure(family_list):
#    
#    # given a name and list of names, create edge list by substring inclusion
#    # create tuples of the form (place_name, name of place containing place_name as substring)
#    def next_edge_set(place_name, place_list):
#        edges = list()
#        for p in place_list:
#            if re.search(place_name, p) != None: edges.append((place_name, p))
#            
#        return edges
#    
#    #family_list.sort(key = len)
#    root_name, children, relations = family_list[0], family_list[1:], []
#    
#    # iterate over elements in family_list in increasing order of string length (assumes sorted list)
#    # applying next_edge_set to popped element and remaining names
#    for i in range(len(family_list)):
#        next_name = family_list.pop(0)
#        relations.extend(next_edge_set(next_name, family_list))
#    
#    return {'root':root_name, 'children':children, 'relations':relations}
#
#
#
#
#def createFilterList(place_list):
#
#    filter_list = createFamilyList(place_list)
#    
#    #temp_filter_list = copy.deepcopy(filter_list)
#    
#    for i, t in enumerate(filter_list):
#        if isinstance(t, list): filter_list[i] = disambiguation_data(createFamilyStructure(t))
#        
#    return filter_list


################ testing ##############
#import copy
## createFilterList
##  - createFilterStructure
##  -- make_family_list
##  - createFamilyStructure
##   -- next_edge_list
#
#temp = placeType(['Crown Heights Plaza','Crown Heights', 'New Haven','South Portland','South Portland Heights Park', 'Portland','West Portland', 'Portland Heights', 'South Portland Heights', 'West Portland Heights', 'South Portland Heights Grove'])
#
#places = ['Crown Heights Plaza','Crown Heights', 'New Haven','South Portland','South Portland Heights Park', 'Portland','West Portland', 'Portland Heights', 'South Portland Heights', 'West Portland Heights', 'South Portland Heights Grove']
#places_copy = copy.copy(places)
#
#'''
#    list of places is turned into a list of families by createFamilyList(). Each family is a list of names. 
#    A list containing a name family is passed to the createFamilyStructure() which converts it to the data 
#    structure that is converted to a disambiguate_data() object. The createFilterList() uses both of these
#    functions to create a list of singletons and disambiguate_data() objects, which is passed on to the 
#    createFilter function, which creates a filter using the SearchGraph objects.
#'''
## createFamilyList
#family_list = createFamilyList(places)
#
## createFamilyStructure
#family_structure = createFamilyStructure(family_list[1])
#
## createFilterList
#filter_list = createFilterList(places)
#
## test on SearchGraph
## initialize SearchGraph 
#G1 = SearchGraph(filter_list[1])
#G1.print_graph()
#
## use prune the search graph
#G1.prune_tree()
#G1.print_graph()
#
#
####### test using placeFilters #######
#
#test_filter = placeFilter(filter_list)
#
#
#string = '''
#        Welcome to West Portland Heights! A suburb of South Portland, 
#        which is next to South Portland Heights but not to be confused with
#        South Portland Heights Grove. The Crown Heights Plaza area is 
#        next to the New Haven school.
#        '''
#    
#
#test_filter.checkFilters(string)
#























