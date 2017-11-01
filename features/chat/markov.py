import gurulhutils
import random

def init( keys ):
    global db
    status, database = gurulhutils.db_init( keys["Database"] )
    db = database.get_collection("taylorswiftdb")

    return status

def help():
  return "Look what you made me do."

def recursion( word ):
    c = db.find_one( { "_word" : word } )
    pop = list( c.keys() )
    w = list( c.values() )
    for i in ["_id", "_word"]:
        try:
            k = pop.index( i )
            pop.pop( k )
            w.pop( k )
        except:
            pass
    try:
        choice = random.choices( population=pop, weights=w )[0]
    except:
        return "."
    if choice == "_end":
        return "."
    else:
        return " " + choice + recursion( choice )

def reply( query ):
    reply = recursion( "_begin" )[1:]

    query.update( { "rinterface" : query["qinterface"], "to": query["from"], "rtype" : "text", "rcontent" : reply } )
    return query
