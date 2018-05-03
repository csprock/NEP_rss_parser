import pandas as pd
import psycopg2
import re

CONN_INFO = {'dbname':'rss_feed_5v2', 'username':'postgres','password':'redalert'}

###################################################
#### import place and county data to database #####
###################################################

# process text file with city and county names
f = open('C:/Users/csprock/Documents/Projects/Data Journalism/News Inequality Project/Data/st23_me_places.txt','r')
lines = []
for l in f:
    temp = l.strip("\n")
    lines.append(temp)
f.close()
lines = list(filter(lambda x: len(x) > 0, lines))


extracts = []
for l in lines:
    temp = l.split("|")
    if re.search('CDP', temp[3]) is None:
        extracts.append( (temp[2], re.sub('town|city|UT','',temp[3]).strip().capitalize(), temp[6].strip() ) )

places = pd.DataFrame.from_records(extracts, columns = ['code','name','county'])


f = open('C:/Users/csprock/Documents/Projects/Data Journalism/News Inequality Project/Data/st23_me_cou.txt','r')
extracts = []
for l in f:
    temp = l.split(",")
    extracts.append( (temp[0], temp[1], temp[2], temp[3]) )
f.close()

extracts = list(map(lambda x: (x[0], x[1] + x[2], x[3]), extracts))
counties = pd.DataFrame.from_records(extracts, columns = ['state','county_FIPS','county'])


#################################################
# loading and parsing Christian's data names

f = open('C:/Users/csprock/Documents/Projects/Data Journalism/News Inequality Project/Data/maine_places.txt')
lines = list()
for l in f: lines.append(l.strip("\n"))

filters = list()
for l in lines:
    temp = l.split(',')
    filters.append(re.sub("'",'',temp[1]))


### filter places by Christian's list

places = places[places['name'].isin(filters)].drop_duplicates()



##### database must be seeded in the following order based on foreign key relationships
# tables seeded by this script have * by them
# - county (*)
# - coverage_region (*)
# -- region_to_county (*)
# -- place (*)
# -- sources
# --- feeds
# ---- article
# ----- place_tags




######### load county data into database 

conn = connectToDatabase(CONN_INFO)
cur = conn.cursor()

for p in counties.iterrows():
    vals = p[1].values
    insert_val = (vals[2], vals[0], vals[1])
    cur.execute("INSERT INTO county VALUES (%s,%s,%s);", insert_val)
    
conn.commit()
conn.close()


####### load city/place names into database

# includes name, county FIPS and place FIPS foreign keyed to county FIPS
# merge county data with place data to get and filter by name, county FIPS and place FIPS
places = pd.merge(places, counties, on = 'county')
col = ['name','county_FIPS','code']
places = places[col]


# write to database
conn = connectToDatabase(CONN_INFO)
cur = conn.cursor()

for p in places.iterrows():
    try:
        vals = p[1].values
        insert_val = (vals[0], vals[1], vals[2])
        cur.execute("INSERT INTO place VALUES (%s,%s,%s);", insert_val)
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        

cur.close()
conn.close()
    
####### adding county and region relationships

conn = connectToDatabase(CONN_INFO)

with conn as con:
    with con.cursor() as cur:
        cur.execute("SELECT * FROM county WHERE state = 'ME';")
        results = cur.fetchall()

cur.close()

cur = conn.cursor()

for r in results:
    cur.execute("INSERT INTO regions_to_county VALUES (%s,%s);", (1, r[2]))
    
conn.commit()
















