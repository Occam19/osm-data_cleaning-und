
# coding: utf-8

# In[3]:


#!/usr/bin/env python


###################
### SQL QUERIES ###
###################
import sqlite3

sqlite3_filename = 'SingaporeMap2.db'
connection = sqlite3.connect(sqlite3_filename)
cursor = connection.cursor()

#Finds the streets with the most OSM objects connected to it.
query = "SELECT tags.value, COUNT(*)          FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags          WHERE type = 'addr' and key = 'street'          GROUP BY tags.value ORDER BY COUNT(*) DESC LIMIT 10;"
#Popular tourist venues
queryA = "SELECT tags.value, COUNT(*) FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags          WHERE type = 'regular' and key = 'tourism' GROUP BY tags.value ORDER BY COUNT(*) DESC;"
#coffee vs tea! - 131 tea, 124 coffee!
queryB = "SELECT COUNT(*) FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags          WHERE type = 'regular' AND key = 'name' AND tags.value LIKE '% coffee %';"
queryC = "SELECT tags.value, COUNT(*) FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags          WHERE type = 'regular' AND key = 'name' AND tags.value LIKE '% tea %'          GROUP BY tags.value ORDER BY COUNT(*) DESC;"
#What are the most popular OSM 'objects' created by users? buildings and highways as it turns out
query1 = "SELECT tags.key, COUNT(*) FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags           WHERE type = 'regular' GROUP BY tags.key ORDER BY COUNT(*) DESC"
#most popular non-regular objects (addr, seamarks)
query2 = "SELECT tags.type, COUNT(*) FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags           GROUP BY tags.type ORDER BY COUNT(*) DESC"
#City name-likes in the data
query3 = ("SELECT tags.value, COUNT(*) as count "
          "FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) tags "
          "WHERE tags.key LIKE '%city%' "
          "GROUP BY tags.value "
          "ORDER BY count DESC "
          "LIMIT 5;")
#All 'cuisines', 'leisure', 'religion'
query5 = ("SELECT tags.value, COUNT(*) as count "
          "FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags "
          "WHERE key = 'religion' GROUP BY tags.value \
          ORDER BY count DESC LIMIT 10;"
)

for val, row in enumerate(cursor.execute(query5)):
    print row

connection.close()

