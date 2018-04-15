import re


def CountMatches(G, string):
    
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
    
    # returns number of matches of expression in a string
    def _computeActual(G, v):
        
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
