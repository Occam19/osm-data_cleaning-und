
# coding: utf-8

# In[ ]:


#!/usr/bin/env python


######################
### CLEANING DATA  ###
######################

import re

def audit_postcode (string):
    #remove all non-numbers
    newstring = re.sub('[^0-9]','', string)
    if len(newstring) == 6:
        return newstring
    #add 0 in front of 9---- 5 length numbers (there are no codes that start with 9 in singapore, miust be 6 numbers)
    #add 0 to end of numbers with 2 00s on end that are 5 length numbers (these are estimates)
    if len(newstring) == 5:
        if newstring[0] == '9':
            newstring2 = '0' + newstring
            print 'ERROR POSTCODE: ' + newstring + ' -> ' + newstring2
            return newstring2
        if newstring[-2:] == '00':
            newstring3 = newstring + '0'
            print 'ERROR POSTCODE: ' + newstring + ' -> ' + newstring3
            return newstring3
    return 'BADCODE'
    
#city names - Singapore, Johor Bahru, Pasir Gudang, Batam, Skudai
CITYNAMES = {"singap" : "Singapore",           # singap to encompass all spellings of singap - ur, or, ore, our
             "johor" : "Johor Bahru",    # written in order of size to choose most likely city for multiple named city
             "pasir" : "Pasir Gudang", 
             "batam" : "Batam", 
             "skudai" : "Skudai"}

def audit_cityname (string, citynames = CITYNAMES):
    string = string.lower()
    for name in citynames.keys():
        if name in string:
            return citynames[name]
    #REMOVE any entries that have numberss in them AND has less than 3 letters in string
    if re.search('^#[\d]{2}-[\d]{2}', string):
            print 'ERROR CITY: ' + string + ' -> ADDR:UNIT'
            return 'unit: ' + string 
    if bool(re.search(r'\d', string)) and bool(sum(c.isalpha() for c in string) < 2):
        print 'ERROR CITY: ' + string + ' -> BADSTRING'
        return 'BADSTRING'
    return string.title()  # capitalize any other city names
    
#Make street names consistent with Rd. -> Road, Ave -> Avenu
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

#audit_streetname helper function, compares each word to mapping dictionary
def check_word_for_streettype (string, dictionary):
    for streettype, mapping in dictionary.items():
        for abbreviation in mapping:
            if string == abbreviation:
                print 'ERROR STREETNAME: ' + string + ' -> ' + streettype
                return streettype
    return string

#split string on space AND '.', for each word -> strip spaces:
def audit_streetname (string):
    audited_addr = ''
    temp_string = string.strip().lower().split()
    for part in temp_string:
        audited_part = check_word_for_streettype(part, MAPPING)
        audited_addr += audited_part.title() + ' '
    return audited_addr[:-1]

def audit_value(value, address_part):
    if address_part == 'postcode':
        return audit_postcode(value)
    elif address_part == 'city':
        return audit_cityname(value)
    elif address_part == 'street':
        return audit_streetname(value)
    return value


# In[ ]:


#!/usr/bin/env python


##################
### XML TO CSV ###
##################

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

OSM_PATH = "singapore.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# Convert XML file structure to python dict structure
def extract_tag_info(element, problem_chars=PROBLEMCHARS):
    tags = []   # Handle secondary tags the same way for both node and way elements
    for tag in element.findall('tag'):
        tag_info = {}
        tag_info['id'] = element.attrib['id']
        tag_info['value'] = tag.attrib['v']
        if problem_chars.match(tag.attrib['k']):
            continue
        elif ':' not in tag.attrib['k']:
            tag_info['key'] = tag.attrib['k']
            tag_info['type'] = 'regular'
        else:
            (tag_info['type'],c,tag_info['key']) = tag.attrib['k'].partition(':')
            if tag_info['type'] == 'addr':
                tag_info['value'] = audit_value(tag_info['value'], tag_info['key'])
                if tag_info['value'] == 'BADSTRING':
                    continue
                if tag_info['value'] == 'addr:unit':
                    tag_info['key'] = 'unit'
                    tag_info['value'] = tag.attrib['v']
        tags.append(tag_info)
    return tags

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    
    if element.tag == 'node':
        for key in node_attr_fields:
            node_attribs[key] = element.attrib[key]
        tags = extract_tag_info(element)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for key in way_attr_fields:
            way_attribs[key] = element.attrib[key]
        tags = extract_tag_info(element)
        for position, nd in enumerate(element.findall('nd')):
            way_node_info = {}
            way_node_info['id'] = element.attrib['id']
            way_node_info['node_id'] = nd.attrib['ref']
            way_node_info['position'] = position
            way_nodes.append(way_node_info)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# Helper Functions
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# Main Function
def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()


        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


process_map(OSM_PATH)


# In[ ]:


#!/usr/bin/env python


#####################
### CSV TO SQL DB ###
#####################

import csv
import sqlite3
from collections import OrderedDict

##function to import any csv file to sqlite3 db, columns_vartype is an OrderedDict with line data
def import_csv(tablename, columns_vartype, filename):

    cursor.execute('''DROP TABLE IF EXISTS {}'''.format(tablename))
    connection.commit()

    # creates strings for CREATE TABLE and INSERT INTO queries of multiple variable amounts
    query1 = ('''CREATE TABLE %s (''' % tablename)
    query2 = ("INSERT INTO %s(" % tablename)
    subquery = "("
    for val in columns_vartype.keys():
        query1 += ('''%s %s NOT NULL''' % (val, columns_vartype[val]))
        if val == columns_vartype.keys()[-1]:
            query1 += (");")
            query2 += ("%s) VALUES " % val)
            subquery += "?);"
        else:
            query1 += (", ")
            query2 += ("%s, " % val)
            subquery += "?, "
    query2 += subquery        
    
    cursor.execute(query1)
    connection.commit()

    
    with open(filename) as fin:
        data = csv.DictReader(fin)
        create_db = []
        for row in data:
            temp_db = []
            for value in columns_vartype.keys():
                temp_db.append(row[value].decode("utf-8"))
            create_db.append(temp_db)
              
    cursor.executemany(query2, create_db)
    connection.commit()
    
## Import data into SQLITE database, using same CSV columns as above
sqlite3_filename = 'SingaporeMap2.db'
connection = sqlite3.connect(sqlite3_filename)
cursor = connection.cursor()

Nodes_Dictionary = OrderedDict([('id', 'INTEGER'), ('lat', 'REAL'), ('lon', 'REAL'), ('user', 'TEXT'), 
                                ('uid', 'INTEGER'), ('version', 'INTEGER'), ('changeset', 'INTEGER'), ('timestamp', 'TEXT')])
Nodes_Tags_Dictionary = OrderedDict([('id', 'INTEGER'), ('key', 'TEXT'), ('value', 'TEXT'), ('type', 'TEXT')])
Ways_Dictionary = OrderedDict([('id', 'INTEGER'), ('user', 'TEXT'), ('uid', 'INTEGER'), ('version', 'INTEGER'), 
                               ('changeset', 'INTEGER'), ('timestamp', 'TEXT')])
Ways_Nodes_Dictionary = OrderedDict([('id', 'INTEGER'), ('node_id', 'INTEGER'), ('position', 'INTEGER')])
Ways_Tags_Dictionary = OrderedDict([('id', 'INTEGER'), ('key', 'TEXT'), ('value', 'TEXT'), ('type', 'TEXT')])

import_csv('Nodes_Tags', Nodes_Tags_Dictionary, 'nodes_tags.csv')
import_csv('Nodes', Nodes_Dictionary, 'nodes.csv')
import_csv('Ways', Ways_Dictionary, 'ways.csv')
import_csv('Ways_Nodes', Ways_Nodes_Dictionary, 'ways_nodes.csv')
import_csv('Ways_Tags', Ways_Tags_Dictionary, 'ways_tags.csv')

connection.close()

