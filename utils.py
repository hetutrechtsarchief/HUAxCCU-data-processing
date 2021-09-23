import datetime,sys

def makeSafeURIPart(s):
  # spreadsheet: [–’&|,\.() ""$/':;]"; "-") ;"-+";"-"); "[.-]$"; ""))
  s = re.sub(r"[–’+?&=|,\.() \"$/']", "-", s) # replace different characters by a dash
  s = re.sub(r"-+", "-", s) # replace multiple dashes by 1 dash
  s = re.sub(r"[^a-zA-Z0-9\-]", "", s) # strip anything else now that is not a alpha or numeric character or a dash
  s = re.sub(r"^-|-$", "", s) # prevent starting or ending with . or -
  if len(s)==0:
    #raise ValueError("makeSafeURIPart results in empty string")
    log.warning("makeSafeURIPart results in empty string")
    # fix this by replacing by 'x' for example
    s="x"
  return s

def isISODate(v):
    try:
        datetime.datetime.strptime(v, '%Y-%m-%d')
        return True
    except ValueError:
      return False # ignore error

def formatSingleValue(v):
  if v.find("http")==0: # startswith
    return f"<{v}>"
  elif isISODate(v):
    return f'"{v}"^^xsd:date'
  else:
    return f'"{v}"'

def formatValue(v):
  s = ", ".join(map(formatSingleValue, v))
  return s

def mergeToObject(obj, row, fieldMapping):
  #this function takes in an existing (or empty object 'obj')
  #the object is *updated* with values from row that are retrieved from fieldMapping
  #the values are stored in arrays with keys from fieldMapping

  for f in fieldMapping.keys():  # f is src key in csv
    v = row[f].strip() # src value
    
    if isinstance(fieldMapping[f], list):
      pred = fieldMapping[f][0]  # pred is dst key as rdf
      typ = fieldMapping[f][1]
      print("!",typ,file=sys.stderr)
    else:
      pred = fieldMapping[f]

    if v: # not empty
      if pred in obj:
        if not v in obj[pred]: # don't duplicate values like ["Q803", "Q803"] etc
          obj[pred].append(v)
      else:
        obj[pred] = [ v ]  # values are aways stored as items in a list even if it's just a single value
  return obj

def createRecord(obj, nsForId, dataType):
  turtle = []
  for f in obj.keys():
    if f=="@id":
      continue
    v = formatValue(obj[f])
    turtle.append(f"  {f} {v}")
  return nsForId + ":" + obj["@id"][0] + " a " + dataType + ' ; \n' + ' ;\n'.join(turtle) + ' .\n'

