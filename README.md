# osm-data_cleaning-und
Udacity Nanodegree data cleaning project (OpenStreetMaps[XML], Python, SQL)

OPENSTREETMAP CLEANING PROJECT

By: Gurpal Sandhu

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
