from rss_config import CONN_INFO
import psycopg2
import json

place_names = ["Westbrook",
	"Biddeford","Saco","Sanford",
	"Acton","Alfred","Arundel","Berwick","Buxton","Cornish",
	"Dayton","Eliot","Hollis","Kennebunk","Kennebunkport",
	"Kittery","Lebanon","Limerick","Limington","Lyman",
	"Newfield","North Berwick","Ogunquit","Old Orchard Beach",
	"Parsonsfield","Baldwin","Bridgton","Brunswick",
	"Cape Elizabeth","Casco","Chebeague Island",
	"Cumberland","Falmouth","Freeport","Frye Island",
	"Gorham","Gray","Harpswell","Harrison","Long Island",
	"Naples","New Gloucester","Pownal",
	"Raymond","Scarborough","Sebago","Windham",
	
{'root':'Portland', 
 'children':['South Portland', 'North Portland', 'West Portland'],
 'relations':[('Portland', 'South Portland'),
              ('Portland', 'North Portland'),
              ('Portland', 'West Portland')]},
 
{'root':'Yarmouth',
 'children':['North Yarmouth'], 
 'relations':[('Yarmouth','North Yarmouth')]},

{'root':'Standish', 
 'children':['Standish Center'],
 'relations':[('Standish', 'Standish Center')]}]
 
 
 

encoder = json.JSONEncoder()
encoded = encoder.encode(place_names)

conn = connectToDatabase(CONN_INFO)

with conn:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO filters VALUES (%s,%s);", ('Portland Press Herald', encoded))
        
        
with conn:
    with conn.cursor() as cur:
        cur.execute("SELECT filters FROM filters;")
        results = cur.fetchone()
        
        
decoder = json.JSONDecoder()
decoded = decoder.decode(results[0])
        
        
        
