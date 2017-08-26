import gurulhutils
from pymongo import MongoClient

debug = True

def init( keys ):
    global medbase

    status, database = gurulhutils.db_init( keys["Database"] )
    if status != "ok":
        return "fail"

    try:
        medbase = database.get_collection("meditants")
        return "ok"
    except:
        return "fail"

def help():
    return "text", "Gurulhu's Meditation Heaven account manager!\nCurrently just creating accounts with:\n/medheav create <login> <email> [<nick> <name> <bio>]"

def med_create( token ):
    global medbase

    if medbase.find_one( {"login": token[0]} ) :
        return "text", "Login already in use", None
    if medbase.find_one( {"email": token[1]} ) :
        return "text", "Email already in use", None

    order = ["login", "email", "nick", "name"]
    meditant = { "valid": False, "banned": False }
    for i in range( min( len( token ), len( order ) ) ):
        meditant.update( { order[i] : token[i] } )

    if len( token ) > len( order ):
        meditant.update( { "bio" : token[4:] } )

    try:
        #medbase.insert_one( meditant )
        return "text", "Meditant acknowledged.", token[1]
    except Exception as e:
        if( debug ): print( "Error in medheav.py, med_create: ", e, flush=True )
        return "text", e, None

def med_auth( token ):
    pass

def med_delete( token ):
    pass

def reply( query ):
    print("Meditant Call", flush = True )

    responses = {
        "create" : med_create,
        "auth" : med_auth,
        "delete" : med_delete
    }

    token = query["qcontent"].split()

    mail = None
    try:
        reply_type, reply, mail = responses[token[1]]( token[2:] )
    except ( KeyError, IndexError ):
        reply_type, reply = help()

    if mail:
        query.update( { "rinterface" : "Email", "to": mail, "rtype" : reply_type, "rcontent" : reply } )
    else:
        query.update( { "rinterface" : query["qinterface"], "to": query["from"], "rtype" : reply_type, "rcontent" : reply } )

    return query
