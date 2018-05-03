

import os, sys
import unittest

if __name__ == '__main__':
    
    mypath = os.path.dirname(os.path.realpath('__file__'))
    sys.path.append(os.path.join(mypath, os.pardir))
    
    from entityFilter.SearchGraph import SearchGraph
    from entityFilter.searchFunctions import CountMatches, NetMatches, returnMatches
    from entityFilter.makeGraphData import makeGraphData


    with open('test_places.txt','r') as r:
        test_places = r.read().split('\n')
        
        
    with open('test_string.txt','r') as f:
        test_string = f.read()
    

class TestSearchFunctions(unittest.TestCase):
    
    def setUp(self):
        
        R, V, E = makeGraphData(test_places)
        self.G = SearchGraph(R, V, E)
        self.G.prune()
        
        self.expected = {'Portland':(5,2), 
                    'South Portland':(2,0),
                    'Portland Heights':(2,0),
                    'South Portland Heights':(2,1),
                    'South Portland Heights Plaza':(1,1),
                    'Oakland':(1,1),
                    'San Jose':(5,3),
                    'South San Jose':(1,0),
                    'South San Jose Terrace':(1,1),
                    'Crown Heights':(1,1),
                    'Crown Heights Plaza':(0,0)}
        
    
    def test_CountMatches(self):
        

        self.G = CountMatches(self.G, test_string)
        
        for k in self.expected.keys():
            
            with self.subTest(k = k):
                self.assertEqual(self.G.V[k].gross, self.expected[k][0])
            
 
            
    def test_NetMatches(self):
        
        self.G = CountMatches(self.G, test_string)
        NetMatches(self.G)
        
        for k in self.expected.keys():
            
            with self.subTest(k = k):
                self.assertEqual(self.G.V[k].actual, self.expected[k][1])
        

        
    def test_returnMatches(self):
        
        results = returnMatches(self.G, test_string)
        
        for k in self.expected.keys():
            
            with self.subTest(k = k):
                self.assertEqual(self.expected[k][1], results[k])


if __name__ == '__main__':
    unittest.main()