import random

def init( keys ):
    return "ok"

def help():
  return "Gurulhu RNG Function \n(A.k.a. RNGurulhu)\n/rng [max]/[min][max]/[min][max][step]"

def reply( query ):
  print("RNG")
  token = query["qcontent"].split()
  reply = "None", None
  try:
      if( len( token ) == 4 ):
          reply = str( random.randrange( float( token[1] ), float( token[2] ), float( token[3] ) ) )
      elif( len( token ) == 3 ):
          reply = str( random.randrange( float( token[1] ), float( token[2] ) ) )
      elif( len( token ) == 2 ):
          reply = str( random.randrange( float( token[1] ) ) )
      else:
          reply = help()
  except:
      reply = help()

  rinterface = query["qinterface"]
  rinterface["specific"].update( { "type" : "text" } )
  query.update( { "rinterface" : { rinterface["name"] : rinterface }, "to": query["from"], "rcontent" : reply } )
  return query
