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

def module_list_init( keys ):
    global module_dictionary

    try:
        status, database = gurulhutils.db_init( keys["Database"] )
        module_list = gurulhutils.import_list( database, "moduledb" )
        module_dictionary = {}
        final_list = []
        for module in module_list:
            try:
                if module["module"].init( keys ) == "ok":
                    module_dictionary.update( { module["call"] : module })
                    final_list.append( module["call"] )
            except Exception as e:
                if( debug ): print( "Error in slave.py, module_list_init: ", e, flush=True )
        return "ok", final_list
    except Exception as e:
        return "fail", []

def connect():
    global server_socket
    server_socket = socket.create_connection( ( socket.gethostbyname( keys["Main"][0] ), int( keys["Main"][1] ) ) )
    gurulhutils.socket_send( server_socket, { "modules" : module_list } )

def listen():
    global server_socket

    while( True ):
        try:
            data = gurulhutils.socket_recv( server_socket )
            print( data )

            if( data == "ping"):
                reply = "pong"
            else:
                reply = module_dictionary[ data["call"] ]["module"].reply( data )

            if( debug ): print( reply )
            gurulhutils.socket_send( server_socket, reply )


        except Exception as e:
            if( debug ): print( "Error in slave.py, listen: ", e, flush=True )
            server_socket.close()
            connect()

keys = keys_get()
status, module_list = module_list_init( keys )
connect()
listen()
