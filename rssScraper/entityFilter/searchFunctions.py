import re


def CountMatches(G, string):
    '''
    Counts the number of times a node name in the graph is contained in the input string.
    
    Input
    -----
    G: SearchGraph object
    string: str
    
    Returns
    ------
    G: modified SearchGraph object
    
    '''
    # returns number of matches of expression in a string
    def _match(rex, string):
        temp = re.findall(rex, string)
        if temp != None:
            return len(temp)
        else:
            return 0
        
        
    for v in G.V:
        G.V[v].gross = _match(v, string)
    
    G.count_status = True
    return G
    


def NetMatches(G):
    '''
    Counts net matches of matched entities by subtracting matches from 
    children to eliminate double countings. Traverses the graph using BFS. 
    
    Input
    -----
    G: modified search graph returned by CountMatches()
    
    Returns
    -------
    G: modified search graph
    '''
    # returns number of matches of expression in a string
    def _computeActual(G, v):
        '''
        Returns number of matches of expression in a string by subtracting
        the number of matches of children from total number of matches.
        
        Input
        -----
        G: SearchGraph object
        v: name of node in SearchGraph
        
        Output
        ------
        net number of matches of the entity represented by vertex v
        '''
        to_subtract = 0
        for u in G.V[v].neighbors:
            to_subtract += G.V[u].gross
        
        return G.V[v].gross - to_subtract
        
    # assert count status has been set to true (CountMatches already run)
    assert G.count_status
        
    for r in G.root:
        
        for v in G.V: G.V[v].visited = False
        F = list()
        G.V[r].visited = True
        F.append(G.V[r])
        to_subtract = 0
        
        while len(F) > 0:
            
            current = F.pop()
            for v in current.neighbors:
                if G.V[v].visited == False:
                    G.V[v].visited = True
                    G.V[v].actual = _computeActual(G, v)   # _computeActual
                    to_subtract += G.V[v].actual
                    F.append(G.V[v]) 
                

        G.V[r].actual = G.V[r].gross - to_subtract
        
    return {v: G.V[v].actual for v in G.V}





def returnMatches(G, string):
    
    G.reset()
    G = CountMatches(G, string)
    matches = NetMatches(G)
    
    return matches
