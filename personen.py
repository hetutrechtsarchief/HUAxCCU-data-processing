#!/usr/bin/env python3 

# this script enriches the data (converting, matching etc) and stores it in lists/dicts
# ready to be converted to turtle by another script

# part of this was already in HetVolkJSON2CSV.py...
# maybe al of it should be in this file reading directly from the json series instead of CSV

# see also test.ttl for a complete example Turtle file

import csv,re,sys
from sys import argv
from utils import * 

entries = []
convicts = {}

with open("header.ttl") as f:
  print(f.read())

with open("combi300.csv") as f:
  reader = csv.DictReader(f) #, fieldnames=header)
  for row in reader:

    # --------------------------------
    # convicts / persons
    # --------------------------------
    personId = row["personId"]  # always exists

    if personId in convicts:
      convict = convicts[personId]
    else:
      convicts[personId] = convict = {}

    mergeToObject(convict, row, {   # update the convict object with new values
      "personId": "@id", #should not be part of the properties but is the 'subject' itself
      "fullname": "rdfs:label",
      "fname": "pnv:givenName",
      "prefix": "pnv:surnamePrefix",
      "sname": "pnv:literalName",
      "occupation": "def:occupation",
      "occupation_norm": "def:occupation",
      "occupation_hisco": "def:occupation",
      "bdate": "sdo:birthDate",
      "bdate-iso": "sdo:birthDate",
      "bplace": "sdo:birthPlace",
      "bplace_norm": "sdo:birthPlace",
      "bplace_wikidata": "sdo:birthPlace"
    })

    # --------------------------------
    # entries
    # --------------------------------

    entry = {}
    entries.append(entry)

    mergeToObject(entry, row, {
      "rec_id": "@id", #should not be part of the properties but is the 'subject' itself
      "personId": ["def:convicts", "@id"], # how to link to person?
      "fullname": "rdfs:label", # how to 'fullname: crime' ?
      "crime": "def:crime",
      "occupation": "def:occupation",
      "age": "def:age",
      "punishment": "def:punishment",
      "from-date": "def:fromDate", 
      "from-date-iso": "def:fromDate", 
      "leave-date": "def:leaveDate", 
      "leave-date-iso": "def:leaveDate", 
      "to-date": "def:toDate", 
      "to-date-iso": "def:toDate", 
      "leave-cause": "def:leaveCause",
      "filename": "def:scan"   # how to scans:NL-UtHUA... with formatValue? based on prefix?
    })


# make Turtle --------------

  for entry in entries:
    turtle = createRecord(entry, "entries", "def:Entry")  # data object, namespace for id, class for subject
    print(turtle)

  for convict in convicts.values(): 
    turtle = createRecord(convict, "convicts", "def:Convict")
    print(turtle)

    # if entries.index(entry)>2:
    #   sys.exit()

  # for personId in convicts.keys():
  #   person = convicts[personId]

  #   print(f"persons:{personId} a sdo:Person ; ")

  #   turtle = []
  #   for f in person.keys():
  #     v = formatValue(person[f])
  #     turtle.append(f"  {f} {v}")

  #   print(' ;\n'.join(turtle) + ' .')

  #   sys.exit()
