import time
import math

def init():
  global seed
  seed = float( time.time() )

def rerroll():
  global seed
  seed = ((( seed * 3.7452 ) + 98.4185) * seed ) % 100000000000000.0000

def number( token ):
  global seed
  try:
      token[1] = float( token[1] )
      token[0] = float( token[0] )

      return ( seed % ( abs( token[0] ) + abs( token[1] ) ) + min( token[1], token[0] ) )
  except:
    try:
      return seed % float( token[1] )
    except:
      return seed

def help():
  return "Gurulhu RNG Function \n(A.k.a. RNGurulhu)\n/rng [max]/[min/max]/[none]"

def reply( query ):
  print("RNG")
  rerroll()
  token = query["qcontent"].replace(',', '.').split()
  if( (len( token ) < 2 ) or ( token[1] == "--help" ) or ( token[1] == "-h" ) ):
    return "text", ( help() )

  raw = str( number( token[-2:] ) )
  raw = raw.split('.')
  token = token[-1].split('.')
  try:
      dif = len( token[1] ) - len( raw[1] )
      if( dif < 0 ):
          raw[1] = raw[1][:dif]
      return "text", query["qinterface"], str( raw[0] + "." + raw[1] )
  except:
      return "text", query["qinterface"], str( int( raw[0] ) )
