import os, sys
import unittest
import csv

if __name__ == '__main__':
    
    mypath = os.path.dirname(os.path.realpath('__file__'))
    sys.path.append(os.path.join(mypath, os.pardir))
    
from rss_scraper.entityFilter.SearchGraph import SearchGraph
from rss_scraper.entityFilter.searchFunctions import CountMatches, NetMatches, returnMatches
from rss_scraper.entityFilter.makeGraphData import makeGraphData


#with open('test_places.txt','r') as r:
#    test_places = r.read().split('\n')
    
    

test_names_ids = list()
with open('test_data/entity_filter/place_names_and_ids.csv', 'r') as testfile:
    reader = csv.reader(testfile, delimiter = ',')
    for r in reader:
        test_names_ids.append((r[0], int(r[1])))
        
test_places = [n[0] for n in test_names_ids]
        
with open('test_data/entity_filter/test_string.txt','r') as f:
    test_string = f.read()
    
with open('test_data/entity_filter/empty_string.txt','r') as f:
    empty_string = f.read()
    

class TestSearchFunctions(unittest.TestCase):
    
    def setUp(self):
        
        R, _, E = makeGraphData(test_places)
        self.G = SearchGraph(R, test_names_ids, E)
        self.G.prune()
        
        self.expected = {'Portland':(5,2,0), 
                    'South Portland':(2,0,0),
                    'Portland Heights':(2,0,0),
                    'South Portland Heights':(2,1,0),
                    'South Portland Heights Plaza':(1,1,0),
                    'Oakland':(1,1,0),
                    'San Jose':(5,3,0),
                    'South San Jose':(1,0,0),
                    'South San Jose Terrace':(1,1,0),
                    'Crown Heights':(1,1,0),
                    'Crown Heights Plaza':(0,0,0),
                    'Portland San Jose':(1,1,0)}
        
        
        self.expected_id_nozeros = {0:2,
                                    2:1,
                                    7:1,
                                    8:1,
                                    9:1,
                                    3:3,
                                    5:1,
                                    10:1}
        
    
    def test_CountMatches(self):
        

        self.G = CountMatches(self.G, test_string)
        
        for k in self.expected.keys():
            
            with self.subTest(k = k):
                self.assertEqual(self.G.V[k].gross, self.expected[k][0])
            
 
            
    def test_NetMatches(self):
        
        self.G = CountMatches(self.G, test_string)
        self.G = NetMatches(self.G)
        
        for k in self.expected.keys():
            
            with self.subTest(k = k):
                self.assertEqual(self.G.V[k].actual, self.expected[k][1])
        

        
    def test_returnMatches(self):
        
        results = returnMatches(self.G, test_string)
        
        for k in self.expected.keys():
            
            with self.subTest(k = k):
                self.assertEqual(self.expected[k][1], results[k])
                
    def test_returnMatches_id_nozeros(self):
        
        results = returnMatches(self.G, test_string, returnType = 'id', returnAll = False)
        
        for k in self.expected_id_nozeros.keys():
            
            with self.subTest(k = k):
                self.assertEqual(self.expected_id_nozeros[k], results[k])
                
    def test_empty_string(self):
        
        results = returnMatches(self.G, empty_string)
        
        for k in self.expected.keys():
            
            with self.subTest(k = k):
                self.assertEqual(self.expected[k][2], results[k])
                
    def test_empty_string_nozeros(self):
        results = returnMatches(self.G, empty_string, returnAll = False)
        self.assertEqual(results, {})
        
    def test_id_only(self):
        
        results = returnMatches(self.G, test_string, returnType = 'id', returnAll = False, id_only = True)
        self.assertEqual(set(results), set(list(self.expected_id_nozeros.keys())))

        
        


if __name__ == '__main__':
    unittest.main()