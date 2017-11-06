import asyncio
import json
import os
import hashlib
import importlib
from pymongo import MongoClient

import time

def sleep( secs ):
    s = int( secs ) * 0.001
    time.sleep( s )

debug = False

def status_check( status, pipe=None, exit_flag=True ):
    if( status != "ok" ):
        if pipe:
            pipe.send("fail")
            pipe.close()
        else:
            print("FAILED.", flush=True)
            print("Exiting . . .", flush=True)
        if( exit_flag ): exit()
    else:
        if pipe:
            pipe.send( "ok" )
        else:
            print("OK.", flush=True)


def db_init( token ):
    try:
        mongo_client = MongoClient( host=token[0], port=int( token[1] ))
        database = mongo_client[ token[2] ]
        database.authenticate( token[3], token[4] )
        return "ok", database
    except Exception as e:
        if( debug ): print( "Error in gurulhutils.py, db_init: ", e, flush=True )
        return "fail", None


def hashfile( f, hash, bs=65536 ):
    f = open( f, "rb" )
    buf = f.read(bs)
    while( len( buf ) > 0 ):
        hash.update(buf)
        buf = f.read(bs)
    return hash.digest()

def import_modules( database, db_name ):
    db = database.get_collection( db_name )

    import_dict = {}

    cursor = db.find()
    for i in range( 0, cursor.count() ):
        name = cursor[i]["name"]
        if os.path.isfile( cursor[i]["path"]):
            if( debug ): print( "Module found: ", name, flush=True )
            if cursor[i]["hash"] == str( hashfile( cursor[i]["path"], hashlib.sha256() ) ):
                try:
                    module = cursor[i]
                    module.update( { "module" : importlib.import_module( cursor[i]["import"] ) } )
                    import_dict.update( { name : module} )
                except Exception as e:
                    if( debug ): print( "Could not import: ", name, "\nReason: ", e, flush=True )
            else:
                if( debug ): print( "File is corrupted: ", name, flush=True)

    return import_dict

def wrap_message( message ):
    return json.dumps( message ).encode("utf-8")

def unwrap_message( message ):
    return json.loads( message.decode("utf-8") )

def format_length( message ):
    reply_len = str( len( message ) )
    while len( reply_len ) < 6:
        reply_len = '0' + reply_len

    return reply_len

def socket_send( socket, message ):
    message_wrap = wrap_message( message )
    message_len = format_length( message_wrap )
    message_len = wrap_message( message_len )
    if( debug ): print( message_len, message_wrap)
    socket.send( message_len )
    socket.send( message_wrap )

def socket_recv( socket ):
    data_len = socket.recv( 8 )
    data_len = unwrap_message( data_len )
    data_len = int( data_len )
    while 1:
        try:
            data = socket.recv( data_len )
            break
        except Exception as e:
            print( "Error in gurulhutils.ocket_recv:", e, flush=True )
    data = unwrap_message( data )
    if( debug ): print( data_len, data )
    return data

def encapsulate_query( query, info ):
    template = {
        "qfrom"         :
            {
                "user"      : info["user"],
                "interface" :
                {
                    "name"      : info["interface"]["name"],
                    "specific"  : info["interface"]["specific"],
                }
            },
        "qcontent"      : info["query"],
        "rto"           :
            [{
                "user"      : "",
                "interface" :
                {
                    "name"      : "",
                    "specific"  : {},
                }
            }],
        "rcontent"      : ""
    }

    return template
