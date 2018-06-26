# osm-data_cleaning-und
Udacity Nanodegree data cleaning project (OpenStreetMaps[XML], Python, SQL)

OPENSTREETMAP CLEANING PROJECT
By: Gurpal Sandhu
Introduction
This project is designed to show my data cleaning and exploration skills using SQL and python. I took open-source data from OpenStreetMaps of the Singapore and the area around it to scrub and analyze. I am interested in visiting Singapore one day.

The steps taken were:

Check over the data. Done at first to find shape in python, later to find attribute data to answer questions with in SQL.
Clean the data. Focused on cleaning addresses, in particular: street-end names, city names, and postcodes. Started by downloading and cleaning a small portion and then applying to main file.
Convert the data into CSV from an XML formatted .OSM file. Then import into SQL db.
Create questions about Singapore I would like to answer, and am able to answer using the data.
Answer questions using SQL queries.
Gave ideas for improvements to data, or alternate uses.
Data Cleaning
The data downloaded from OpenStreetMaps is stored in an .osm file, size of 321 MB. An .osm file, as stated by the OpenStreetMaps wikipedia, uses the XML collapsible datastructure, along with a 'type:value' format to keep data tidy. I focused on cleaning the addresses of each node, since the address was what was input by hand by (fallible) human volunteers; in particular, the street-end names, city names, and postcodes.

Street-End Names
A mapping was used to clean up the different end names. Since I had no awareness of typical Singaporean end names, I had to go back (after exploring with SQL) to include end-names like Lorong and Jalan alongside end-names like Street and Drive.

MAPPING = {
    'Street':['str', 'st.', 'st'],
    'Road':['rd', 'rd.'],
    'Avenue':['ave', 'av', 'av.', 'ave.'],
    'Jalan':['jl', 'jln', 'jl.'],
    'Lane':['ln', 'ln.'],
    'Drive':['dr', 'dr.'],
    'Lorong':['lr', 'lr.'],
    'Square':['sq', 'sq.']
}
Postcodes
Postcodes in Singapore are a 6 number string with the first two numbers the general area, and the last four the exact location. Some online research showed me that the 81 postcode area is the newest postal sector, and in my SQL queries, I noticed that it had many of the bad post codes. The steps used to clean the codes were:

Remove all non-numbers. Done using regex (regular expressions module in python).

 newstring = re.sub('[^0-9]','', string)
Add 0 in front of 9---- 5 length numbers (there are no codes that start with 9 in Singapore)

Add 0 to end of numbers with 2 00s on end that are 5 length numbers (these are estimations)
Rest are removed, replaced with ''.
City Names
Oftentimes, extra information would be put here instead of or alongside the cityname. First, any city names with any numbers in the string AND with fewer letters than 3 were automatically deleted. Regex was used here. Then, a mapping was used to fix the rest of the city names. The majority of names are the 5 big ones:

CITYNAMES = {"singap" : "Singapore",           # singap to encompass all spellings of singap - ur, or, ore, our
             "johor bahru" : "Johor Bahru",    # written in order of size to choose most likely city for multiple named city
             "pasir gudang" : "Pasir Gudang", 
             "batam" : "Batam", 
             "skudai" : "Skudai"}
There were many variations in the data for city names(ie. Singapore/singapur). As a result, if it had 'singap', 'bahru', 'pasir', 'batam', 'skudai' anywhere in the string, it was changed to align. Finally, the first letter was changed to uppercase - for any city name.

Data Importing / SQL Overview
The map data was extracted from an XML format, and changed from XML to python's dict structure. Then, the values were audited and cleaned as shown above. The data was separated into 5 csv files, and finally imported into SQL under the same headers. I also tried importing directly from the command line, but the encoding was finicky. The CSV / SQL column names are below.

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
File Sizes
Singapore.osm - 321 MB nodes, nodes_tags, ways, ways_nodes, ways_tags . csv - 201 MB SingaporeMap.db - 182 MB

Node and Ways Count
sqlite> SELECT COUNT(*) FROM nodes;

Nodes : 1482437

sqlite> SELECT COUNT(*) FROM ways;

Ways : 233033
Unique Contributor Data
sqlite > SELECT COUNT(DISTINCT(tags.uid))
         FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) AS tags;

Total Contributor Count : 2057

sqlite > SELECT tags.user, COUNT(*) as num
         FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) AS tags
         GROUP BY tags.user ORDER BY num DESC
         LIMIT 5;

Top 5 Contributors:
    JaLooNz, 395146
    berjaya, 117636
    rene78, 78269
    cboothroyd, 73129
    lmum, 44070
Answering Questions about Singapore
Major Streets
I wanted to know what the major streets of Singapore were. I looked for streets with the most OSM objects connected to it.

sqlite > SELECT tags.value, COUNT(*) 
         FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags 
         WHERE type = 'addr' and key = 'street' 
         GROUP BY tags.value ORDER BY COUNT(*) DESC LIMIT 10;

Joo Chiat Road, 347
Geylang Road, 261
Serangoon Road, 246
Jalan Senang, 234
South Bridge Road, 197
Jalan Besar, 192
North Bridge Road, 188
Tanjong Pagar Road, 181
Arab Street, 168
Westwood Crescent, 165
Tea vs Coffee Preference
Another question I had was whether a highly developed Eastern city like Singapore prefered coffee, a Western-preferred drink, or tea, an Eastern one.

sqlite > SELECT COUNT(*) 
         FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags
         WHERE type = 'regular' AND key = 'name' AND tags.value LIKE '% coffee %';

31

sqlite > SELECT COUNT(*) 
         FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags
         WHERE type = 'regular' AND key = 'name' AND tags.value LIKE '% tea %';"

24
Top Leisure Activities
sqlite > SELECT tags.value, COUNT(*) as count
         FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags
         WHERE key = 'leisure' GROUP BY tags.value
         ORDER BY count DESC LIMIT 10;

swimming_pool, 1271
pitch, 1056
park, 648
playground, 276
sports_centre, 110
park_connector, 83
fitness_centre, 76
golf_course, 51
garden, 48
recreation_ground', 48
Top Religions
sqlite > SELECT tags.value, COUNT(*) as count
         FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags
         WHERE key = 'religion' GROUP BY tags.value
         ORDER BY count DESC LIMIT 10;

muslim, 591
christian, 245
buddhist, 106
hindu, 23
taoist, 11
jewish, 4
sikh, 4
shinto, 1
Most Popular Foods
sqlite > SELECT tags.value, COUNT(*) as count
         FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags
         WHERE key = cuisine' GROUP BY tags.value
         ORDER BY count DESC LIMIT 10;

chinese, 170
burger, 96
japanese, 86
pizza, 64
coffee_shop, 57
chicken, 55
asian, 50
indian, 50
korean, 49
italian, 47
Data Suggestions
Much of the frustrations I had from cleaning the data came from the city names, with many incorrectly spelled major city names - not to mention house numbers, zipcodes, or random information about the location. I believe this was because users are made to input cities manually and are given no extra boxes to put notes on the location. If Open Street Maps had contibutors choose from a drop-down menu to input their city choice, with an 'other' option for extranous situations, much of the headache from inconsistant city naming across the board could be avoided. This would work extremely well if the user's current location is known, or he is inputting information for a major urban center.

I was extremently interested in the 'leisure' tag, to find out what Singaporeans do for fun. Unfortunately, the majority of the data is unusable, with general values such as 'hotel' and 'attraction'. There's an opportunity there for more specific information to be presented.

    sqlite > SELECT tags.value, COUNT(*) \
             FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags
             WHERE type = 'regular' and key = 'tourism' 
             GROUP BY tags.value ORDER BY COUNT(*) DESC LIMIT 5;

    hotel, 563
    attraction, 274
    hostel, 82
    information, 74
    viewpoint, 59
Conclusion
I have a firmer grasp on good data cleaning habits after this project, with a better sense of the large trial-retrial aspect of auditing. Additionally, I learned alot about Singapore from analyzing the street data, solidifying my wish to travel there one day.

References:

https://docs.python.org/3/library
https://wiki.openstreetmap.org/wiki/Main_Page
https://discussions.udacity.com/
