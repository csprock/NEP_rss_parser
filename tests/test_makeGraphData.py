import unittest
import os, sys

if __name__ == '__main__':
    
    mypath = os.path.dirname(os.path.realpath('__file__'))
    sys.path.append(os.path.join(mypath, os.pardir))


from rssScraper.entityFilter.makeGraphData import nameType, next_edge_set, makeEdgeSet

with open('test_data/entity_filter/test_places.txt','r') as r:
    test_places = r.read().split('\n')
    
    

class TestFilterCreationMethods(unittest.TestCase):
    
    
    def test_placeType(self):
        
        roots, children, singles = nameType(test_places)
        
        with self.subTest():
            self.assertEqual(set(roots), {'Portland','San Jose','Crown Heights'})
        
        with self.subTest():
            self.assertEqual(set(children), {'South Portland','South San Jose',
                                        'Portland Heights','Portland San Jose',
                                        'Crown Heights Plaza','South San Jose Terrace',
                                        'South Portland Heights','South Portland Heights Plaza'})
        
        with self.subTest():
            self.assertEqual(set(singles), {'Oakland'})


    def test_next_edge_set(self):
        
        edge_list = next_edge_set('Portland', ['South Portland', 
                                               'Oakland', 
                                               'South Portland Heights'])

        self.assertEqual(set(edge_list), {('Portland','South Portland'), ('Portland','South Portland Heights')})
        
        
    def test_makeEdgeList(self):
        
        edge_list = makeEdgeSet(['South Portland','Oakland',
                                 'South Portland Heights','Portland',
                                 'Crown Heights', 'Crown Heights Plaza'])
                
        self.assertEqual(set(edge_list), {('Portland','South Portland'),('Portland','South Portland Heights'),
                           ('South Portland','South Portland Heights'),
                           ('Crown Heights', 'Crown Heights Plaza')})
        

if __name__ == "__main__":
    unittest.main()