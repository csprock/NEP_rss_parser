

class EntityVertex:
    '''
    Vertex object class for use with SearchGraph. Each vertex represents a named entity
    to be searched for in strings. 
    '''
    def __init__(self, n):
        self.name = n[0]
        self.id = n[1]

        self.neighbors = set()
        self.visited = False
        
        self.gross = int()
        self.actual = int()
        
    def add_neighbor(self, u):
        
        assert isinstance(u, str) or isinstance(u, int)
        if u not in self.neighbors:
            self.neighbors.update([u])
            

class SearchGraph:
    '''
    Data structure for storing string-substring relationships between named entities for
    the purpose of correctly counting the number of entities without overcounting. 
    '''
    def __init__(self, root, V, E, directed = True):
        """ 
        V must be a list of tuples of the form (name, id) and E must be a list of tuples. For directed graphs,
        the tuple (u,v) represents are arc from u to v.
        """
        self.count_status = False
        self.V = {n[0]:EntityVertex(n) for n in V}
        self.root = root
        
        if directed:
            
            for v, u in E:
                if v in self.V and u in self.V:
                    self.V[v].add_neighbor(u)
                
        else:
            for v, u in E:
                if v in self.V and u in self.V:
                    self.V[v].add_neighbor(u)
                    self.V[u].add_neighbor(v)
                    

    def print(self):
        
        for v in self.V:
            print("v = %s, N(v) = %s" % (v, self.V[v].neighbors))
            
        
    # resets graph for next search
    def reset(self):
        self.count_status = False
        
        for v in self.V:
            self.V[v].gross = int()
            self.V[v].actual = int()
            self.V[v].visited = False
        

    
    # deletes hypotenuse of directed triangles
    def prune(self):
        
        for v in self.V:
            to_prune = set()
            
            for u in self.V[v].neighbors:
                to_prune.update(self.V[v].neighbors.intersection(self.V[u].neighbors))
                
            self.V[v].neighbors = self.V[v].neighbors - to_prune
    
        

            

#################### functions for search graph ###############################
#def PruneTree(G):
#    
#    for v in G.V:
#        _PruneNeighbors(G, v)
#    
#
#    
#def _PruneNeighbors(G,v):
#    to_prune = set()
#    for u in G.V[v].neighbors:
#        to_prune.update(G.V[v].neighbors.intersection(G.V[u].neighbors))
#        
#    
#    G.V[v].neighbors = G.V[v].neighbors - to_prune

#
#
#R, E, V = makeGraphData(test_places)
#
#SG = Graph(R, V, E)
#PruneTree(SG)
#CountMatches(SG, test_string)
#
#for v in SG.V:
#    print("%s, %s" % (v, SG.V[v].gross))
#
#NetMatches(SG)
#for v in SG.V:
#    print("%s, %s" % (v, SG.V[v].actual))
#
#
#
#
#
#S = {'a','b','d'}
#for v in S:
#    print(v)




#def BFS(G, s):
#    """ designed to be used with Graph object """
#    assert isinstance(G, Graph)
#    
#    # reset 
#    for v in G.V:
#        G.V[v].visited = False
#    
#    
#    F = list()
#    G.V[s].visited = True
#    F.append(G.V[s])
#    
#    while len(F) > 0:
#        
#        current = F.pop()
#        for v in current.neighbors:
#            if G.V[v].visited == False:
#                G.V[v].visited = True
#                F.append(G.V[v])
#                
#                
#
#def DFS_util(G, s):
#    """ designed to used with Graph object"""
#    G.V[s].visited = True
#    for u in G.V[s].neighbors:
#        if G.V[u].visited == False:
#            G.V[u].visited = True
#            DFS_util(G, u)
#
#
#def DFS(G):
#    """ designed to be used with Graph object """
#    # reset 
#    for v in G.V:
#        G.V[v].visited = False        
#    
#    for v in G.V:
#        if G.V[v].visited == False:
#            DFS_util(G, v)
#
#
#V = ['a','b','c','d','e']        
#        
#E = [('a','d'),
#     ('a','c'),
#     ('a','e'),
#     ('b','d'),
#     ('d','c'),
#     ('d','e'),
#     ('e','c')]
#
#G = Graph(None, V,E,directed = False)
#
#DFS(G)
#
#
#
#for u in G.V:
#    print(G.V[u].visited)














