import re
from SearchGraph import *
from placeFilter import placeFilter


def createFilterStructure(place_list):
    
    indicators = dict()
    for p in place_list:
        indicators[p] = {'is_parent':0, 'is_child':0}
        
    for i in range(0,len(place_list)):
        current = place_list.pop(0)
        for p in place_list:
            if re.search(current, p) != None:
                indicators[current]['is_parent'] , indicators[p]['is_child'] = 1, 1
    
    roots, singles, children, data_list = [],[],[],[]

    for p in indicators:
        
        if indicators[p]['is_child'] == 0 and indicators[p]['is_parent'] == 1:
            roots.append(p)
        elif indicators[p]['is_child'] == 0 and indicators[p]['is_parent'] == 0:
            singles.append(p)
        else:
            children.append(p)
        
    
    for r in roots:
        temp = make_place_list(r, children)
        data_list.append(temp)
        
    data_list.extend(singles)
    return data_list
        
        
        

def make_place_list(rt, cld):
    
    place_list, child_list = [rt], []
    
    for c in cld:
        if re.search(rt, c) != None:
            child_list.append(c)
           
    place_list.extend(child_list)
    return place_list
    
def createFullStructure(place_list):
    
    def _next_edge_set(place_name, place_list):
        edges = []
        for p in place_list:
            if re.search(place_name, p) != None:
                edges.append((place_name, p))
            
        return edges
    
    place_list.sort(key = len)
    root_name, children, relations = place_list[0], place_list[1:], []
    
    for i in range(0, len(place_list)):
        
        next_name = place_list.pop(0)
        relations.extend(_next_edge_set(next_name, place_list))
    
    return {'root':root_name, 'children':children, 'relations':relations}




def createFilterList(place_list):

    filter_list = createFilterStructure(place_list)
    
    #temp_filter_list = copy.deepcopy(filter_list)
    
    
    for i, t in enumerate(filter_list):
        if isinstance(t, list):
            #temp2 = createFullStructure(t)
            filter_list[i] = disambiguation_data(createFullStructure(t))
        
    return filter_list


############### testing ##############


#places = ['Crown Heights','Crown Heights Plaza','New Haven','Portland','South Portland', 'West Portland', 'Portland Heights', 'South Portland Heights', 'South Portland Heights Park', 'West Portland Heights', 'South Portland Heights Grove']
#
#
#
#
#filter_list, place_dict = createFilterList(places)
#
#
#G1 = SearchGraph(filter_list[1])
#G1.print_graph()
#G1.prune_tree()
#
#G1.print_graph()
#
#
#
#pf = placeFilter(filter_list)























