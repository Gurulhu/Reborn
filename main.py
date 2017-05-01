import os
import multiprocessing
from pymongo import MongoClient
from interfaces import interface_handler as int_hand
from botnet import botnet_handler as botnet_hand
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

def interface_handler_init( queries, replies, keys ):
    try:
        interface_handler_read_pipe_child, interface_handler_write_pipe_parent = multiprocessing.Pipe( False )
        interface_handler_read_pipe_parent, interface_handler_write_pipe_child = multiprocessing.Pipe( False )

        interface_handler_daemon = multiprocessing.Process( target=int_hand.daemonize, args=( interface_handler_read_pipe_child, interface_handler_write_pipe_child, queries, replies, keys ) )
        interface_handler_daemon.start()

        interface_handler = { "name": "Interface Handler",
            "process": interface_handler_daemon,
            "write_pipe" : interface_handler_write_pipe_parent,
            "read_pipe" : interface_handler_read_pipe_parent,
            "status" : "up" }

        print( "OK", flush=True )
        print( "Waiting on Interfaces . . . ", flush=True )

        interface_handler["read_pipe"].poll()
        if( interface_handler["read_pipe"].recv() == "ok" ):
            return "ok", interface_handler
        else:
            return "fail", interface_handler
    except Exception as e:
        if( debug ): print( "Error in main.py, interface_handler_init: ", e, flush=True )
        return "fail", None

def botnet_handler_init( replies, keys ):
    try:
        botnet_handler_read_pipe_child, botnet_handler_write_pipe_parent = multiprocessing.Pipe( False )
        botnet_handler_read_pipe_parent, botnet_handler_write_pipe_child = multiprocessing.Pipe( False )

        botnet_handler_daemon = multiprocessing.Process( target=botnet_hand.daemonize, args=( botnet_handler_read_pipe_child, botnet_handler_write_pipe_child, queries, replies, keys ) )
        botnet_handler_daemon.start()

        botnet_handler = { "name": "botnet Handler",
            "process": botnet_handler_daemon,
            "write_pipe" : botnet_handler_write_pipe_parent,
            "read_pipe" : botnet_handler_read_pipe_parent,
            "status" : "pending" }

        botnet_handler["read_pipe"].poll()
        if( botnet_handler["read_pipe"].recv() == "ok" ):
            botnet_handler.update( { "status" : "up" } )
            return "ok", botnet_handler
        else:
            botnet_handler.update( { "status" : "failed" } )
            return "fail", botnet_handler
    except Exception as e:
        if( debug ): print( "Error in main.py, botnet_handler_init: ", e, flush=True )
        return "fail", None

if __name__ == "__main__":
    keys = keys_get()
    queries = multiprocessing.Queue()
    replies = multiprocessing.Queue()

    print("Starting Database connection . . . ", end="", flush=True)
    status, database = gurulhutils.db_init( keys["Database"] )
    gurulhutils.status_check( status )

    print("Starting Interface Handler . . . ", end="", flush=True)
    status, interface_handler = interface_handler_init( queries, replies, keys )
    gurulhutils.status_check( status )

    print("Starting BotNet Handler . . . ", end="", flush=True)
    status, botnet_handler = botnet_handler_init( replies, keys )
    gurulhutils.status_check( status )

    while( status != "down" ):
        try:
            gurulhutils.sleep( 1 )
        except Exception as e:
            if( debug ): print( "Error in main.py, main: ", e, flush=True )
