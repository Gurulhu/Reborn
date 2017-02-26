import os
import socket
import json
import gurulhutils

debug = True

def keys_get():
    keys = {}
    try:
        count = 0
        while( True ):
            args = os.environ['init_value_' + str( count )].split(",")
            keys.update( { os.environ['init_key_' + str( count )]: args } )
            count += 1
    except:
        pass
    return keys

def module_list_init():
    global module_dictionary

    try:
        status, database = gurulhutils.db_init( [ keys["Database"][0], int( keys["Database"][1] ), keys["Database"][2], keys["Database"][3], keys["Database"][4] ] )
        module_list = gurulhutils.import_list( database, "moduledb" )
        module_dictionary = {}
        final_list = []
        for module in module_list:
            try:
                module["module"].init()
                module_dictionary.update( { module["call"] : module })
                final_list.append( module["call"] )
            except Exception as e:
                if( debug ): print( "Error in slave.py, module_list_init: ", e, flush=True )
        return "ok", final_list
    except Exception as e:
        return "fail", []

def connect():
    global server_socket
    server_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    server_socket.connect( ( keys["Main"][0], int( keys["Main"][1] ) ) )

    server_socket.send( gurulhutils.wrap_message( { "modules" : module_list } ) )

def listen():
    global server_socket

    while( True ):
        try:
            data = server_socket.recv( 4096 )
            data = gurulhutils.unwrap_message( data )

            if( data == "ping"):
                server_socket.send( gurulhutils.wrap_message( "pong" ) )
            else:
                reply_interface, reply_type, reply = module_dictionary[ data["call"] ]["module"].reply( data )
                data.update( { "rinterface" : reply_interface, "rtype" : reply_type, "rcontent" : reply } )
                print( reply )
                reply =  gurulhutils.wrap_message( data )
                server_socket.send( reply )

        except Exception as e:
            if( debug ): print( "Error in slave.py, listen: ", e, flush=True )
            server_socket.close()
            connect()

keys = keys_get()
status, module_list = module_list_init()
connect()
listen()
