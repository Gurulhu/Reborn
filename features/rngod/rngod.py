import random

def init():
    pass

def help():
  return "Gurulhu RNG Function \n(A.k.a. RNGurulhu)\n/rng [max]/[min][max]/[min][max][step]"

def reply( query ):
  print("RNG")
  token = query["qcontent"].split()
  if( len( token ) == 4 ):
      return query["qinterface"], "text", str( random.randrange( float( token[1] ), float( token[2] ), float( token[3] ) ) )
  elif( len( token ) == 3 ):
      return query["qinterface"], "text", str( random.randrange( float( token[1] ), float( token[2] ) ) )
  elif( len( token ) == 2 ):
      return query["qinterface"], "text", str( random.randrange( float( token[1] ) ) )
  else:
      return query["qinterface"], "text", help()
