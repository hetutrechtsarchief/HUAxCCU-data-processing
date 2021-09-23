#!/usr/bin/env python3
import json,csv,sys,re,datetime,hashlib,uuid
from sys import argv

def generateGUID():
  return uuid.uuid4().hex.upper()

outputheader = [ "rec_id", "serie", "file_id", "filename", "personId", "fullname", "bdate-iso","age","bplace_norm", "bplace_wikidata", "occupation", "occupation_norm", "occupation_hisco", "crime","punishment","from-date-iso", "to-date-iso", "duration-days", "leave-date-iso", "leave-cause", "transit", "fname", "prefix", "sname", "bplace", "bdate", "from-date", "to-date", "leave-date"]

series = [ "Gansstraat-1910-1920", "Wolvenplein-1900-1920" ]

recId = 1
filenames = {}
locaties = {}
beroepen = {}

output = csv.DictWriter(open('combi.csv','w'), fieldnames=outputheader, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
output.writeheader()


# read CSV file containing filenames of scans and previously generated file IDs
for serie in series:
  with open("IDs/"+serie+".csv") as f:
    reader = csv.DictReader(f, fieldnames=["uuid","name","width","height","link"])
    for row in reader:
      filenames[row["uuid"]] = row["name"]

# read CSV 'locations'
for serie in series:
  with open("locaties-genormaliseerd-wikidata.csv") as f:
    reader = csv.DictReader(f, fieldnames=["locatie","normalised","wikidata"])
    for row in reader:
      locaties[row["locatie"]] = row

# read CSV file 'beroepen'
for serie in series:
  with open("hisco-beroepen-matches.csv") as f:
    reader = csv.DictReader(f, fieldnames=["beroep","normalised","hisco"])
    for row in reader:
      beroepen[row["beroep"]] = row

# read results from HetVolk.org
for serie in series:

  with open("data/"+serie+".json") as f:
    data = json.load(f)

    for record in data:
      id = record["id"]

      if isinstance(record["antwoord"], dict):
        persons = record["antwoord"]["person"]

        for person in persons:

          #record id
          person["rec_id"] = recId
          recId = recId + 1

          #serie
          person["serie"] = serie

          #scan filename and id
          person["file_id"] = id
          person["filename"] = filenames[id]

          #convert dates to iso, ignore when invalid
          for datefield in ["bdate", "from-date", "to-date", "leave-date"]:
            try:
              if datefield in person:
                dt = datetime.datetime.strptime(person[datefield], '%d-%m-%Y').strftime('%Y-%m-%d')
                person[datefield+"-iso"] = dt
            except ValueError:
              pass # just skip invalid/incomplete dates

          #if valid iso bdate and lastname, save a hash as person identifier
          if "bdate-iso" in person and "sname" in person:
            pid = (person["sname"].lower()+"-"+person["bdate-iso"]).encode('utf-8')
            person["personId"] = hashlib.md5(pid).hexdigest()
          else:
            person["personId"] = generateGUID() # random GUID (in capitals)

          #normalise location and link with wikidata
          if "bplace" in person and person["bplace"] in locaties:
            person["bplace_norm"] = locaties[person["bplace"]]["normalised"]
            person["bplace_wikidata"] = "http://www.wikidata.org/entity/"+locaties[person["bplace"]]["wikidata"]

          #normalise beroep and link with hisco
          if "occupation" in person and person["occupation"] in beroepen:
            person["occupation_norm"] = beroepen[person["occupation"]]["normalised"]
            person["occupation_hisco"] = beroepen[person["occupation"]]["hisco"]

          #age
          if "bdate-iso" in person and "from-date-iso" in person:
            bdate = datetime.datetime.strptime(person["bdate-iso"], '%Y-%m-%d')  # sorry, need to parse again
            fromdate = datetime.datetime.strptime(person["from-date-iso"], '%Y-%m-%d')  # sorry, need to parse again
            person["age"] = int(abs((fromdate - bdate).days)/365)

          #duration
          if "to-date-iso" in person and "from-date-iso" in person:
            todate = datetime.datetime.strptime(person["to-date-iso"], '%Y-%m-%d')  # sorry, need to parse again
            fromdate = datetime.datetime.strptime(person["from-date-iso"], '%Y-%m-%d')  # sorry, need to parse again
            person["duration-days"] = abs(todate - fromdate).days

          #name
          parts = []
          for field in ["fname", "prefix", "sname"]:
            if field in person:
              parts.append(person[field])
          person["fullname"] = " ".join(parts)

          #output to csv
          output.writerow(person)

          # if recId>100:
          #   sys.exit()

print("Ready creating combi.csv")

