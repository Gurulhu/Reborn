import os
import multiprocessing
import threading
import importlib
from pymongo import MongoClient
import gurulhutils

debug = True



def interface_init( interface, queue, keys, read_pipe = None, write_pipe = None ):
    print( "Starting " + interface["name"] + " Interface . . . ", end="", flush=True )
    interface_read_pipe_parent, interface_write_pipe_child = multiprocessing.Pipe( False )
    interface_read_pipe_child, interface_write_pipe_parent = multiprocessing.Pipe( False )
    interface_process = multiprocessing.Process( target=interface["module"].daemonize, args=( interface_read_pipe_child, interface_write_pipe_child, queue, keys[ interface["name"] ] ) )
    interface_process.start()
    interface_read_pipe_parent.poll()
    if( interface_read_pipe_parent.recv() == "ok" ):
        interface.update( {
            "process": interface_process,
            "write_pipe": interface_write_pipe_parent,
            "read_pipe": interface_read_pipe_parent,
            "status": "up" } )
        print( "OK", flush=True )
    else:
        interface.update( { "status": "failed" } )
        print( "FAILED", flush=True )

    return interface

def interface_list_init( queue, keys ):
    global interface_list

    status, database = gurulhutils.db_init( keys["Database"] )
    if( status != "ok" ):
        return "fail"

    interface_list = gurulhutils.import_list( database, "interfacedb" )

    for interface in interface_list:
        interface =  interface_init( interface, queue, keys )
    return "ok"

def shutdown():
    pass

def route_replies( replies ):
    global interface_list
    while( True ):
        query = replies.get()
        if( query["rtype"] and query["rtype"] != "None" ):
            for interface in interface_list:
                if( query["rinterface"] == interface["name"] ):
                    interface["write_pipe"].send( query )
                    break


def daemonize( read_pipe, write_pipe, queries, replies, keys ):
    global interface_list
    #Creates interface_list sequencially
    status = interface_list_init( queries, keys )
    gurulhutils.status_check( status, write_pipe )

    router_thread = threading.Thread( target= route_replies, args = [ replies ], daemon = True )
    router_thread.start()

    try:
        while( status != "down" ):

            for interface in interface_list:
                if( interface["status"] == "down" ):
                    print( interface["name"] + " Interface is down.", flush=True )
                    interface["read_pipe"].close()
                    interface["write_pipe"].close()
                    interface = interface_handler_init

    except Exception as e:
        if( debug ): print( "Error in interface_handler.py, daemonize(): ", e, flush=True )
