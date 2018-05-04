import unittest
import os, sys

if __name__ == '__main__':
    mypath = os.path.dirname(os.path.realpath('__file__'))
    sys.path.append(os.path.join(mypath, os.pardir))


from entityFilter.makeGraphData import makeGraphData
from entityFilter.SearchGraph import SearchGraph


with open('test_places.txt','r') as r:
    test_places = r.read().split('\n')
    
import csv

test_names_ids = list()
with open('place_names_and_ids.csv', 'r') as testfile:
    reader = csv.reader(testfile, delimiter = ',')
    for r in reader:
        test_names_ids.append((r[0], int(r[1])))
    

class TestSearchGraph(unittest.TestCase):
    
    def setUp(self):
        
        R, V, E = makeGraphData(test_places)
        self.G = SearchGraph(R,test_names_ids,E)
        
        
        
    def test_neighbors(self):
        
        #### test neighbors of root vertices ####
        
        
        with self.subTest():
            self.assertEqual(self.G.V['Portland'].neighbors, {'South Portland','Portland Heights',
                             'South Portland Heights','South Portland Heights Plaza','Portland San Jose'})
        
        
        with self.subTest():
            self.assertEqual(self.G.V['San Jose'].neighbors, {'Portland San Jose','South San Jose','South San Jose Terrace'})
        
        
        with self.subTest():
            self.assertEqual(self.G.V['Crown Heights'].neighbors, {'Crown Heights Plaza'})
            
        with self.subTest():
            self.assertEqual(self.G.V['Oakland'].neighbors, set())
        
                    
        
        
    def test_pruning(self):
        
        self.G.prune()
        
        with self.subTest():
            self.assertEqual(self.G.V['Portland'].neighbors, {'South Portland','Portland San Jose','Portland Heights'})
            
        with self.subTest():
            self.assertEqual(self.G.V['San Jose'].neighbors, {'Portland San Jose','South San Jose'})
            
            
    
            
if __name__ == '__main__':
    unittest.main()