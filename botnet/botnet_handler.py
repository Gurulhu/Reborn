import socket
import json
import threading
import gurulhutils

debug = True

def server_setup():
    global server_socket

    try:
        server_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        server_socket.bind( ( socket.gethostname(), 13031 ) )
        server_socket.listen( 80 )
        server_socket.setblocking(False)

        return "ok"
    except Exception as e:
        if( debug ): print( "Error in botnet_handler.py, server_setup: ", e, flush=True )
        return "fail"

def server_loop():
    global server_socket
    global slave_list
    global module_list

    while( True ):
        gurulhutils.sleep( 1 )
        try:
            slave_socket, address = server_socket.accept()
            slave_socket.setblocking( True )
            slave = { "socket" : slave_socket,
                    "address" : address }
            handshake = slave_socket.recv( 4096 )

            slave.update( gurulhutils.unwrap_message( handshake ) )

            slave_socket.send( gurulhutils.wrap_message( "ping" ) )
            pong = slave_socket.recv( 4096 )

            if( gurulhutils.unwrap_message( pong ) == "pong" ):
                for module in slave["modules"]:
                    if module not in module_list:
                        module_list.append( module )

                slave_socket.setblocking( False )
                slave_list.append( slave )

        except BlockingIOError:
            pass
        except Exception as e:
            if( debug ): print( "Error in botnet_handler.py, server_loop: ", e, flush=True )
            server_socket.close()

def schedule( query, call ):
    query.update( { "call" : call } )

    for slave in slave_list:
        if call in slave["modules"]:
            slave["socket"].send( gurulhutils.wrap_message( query ) )
            return "ok"
    return "fail"

def route_loop( write_pipe, queries ):
    while( True ):
        gurulhutils.sleep( 1 )
        query = queries.get()
        if( query["qtype"] == "text" ):
            token = query["qcontent"].split(" ")
            print( module_list )
            if token[0] in module_list:
                schedule( query, token[0] )
            elif( token[0] == "/botctrl" ):
                write_pipe.send( query )
            elif( token[0].find("/") < 0 ):
                schedule( query, "chat" )
            else:
                print( token[0] )
                query.update( { "rtype" : "text", "rcontent" : "Sorry, I have no active module to recognize this." } )
                write_pipe.send( query )

def listen_loop( replies ):
    global slave_list
    while( True ):
        gurulhutils.sleep( 1 )
        for slave in slave_list:
            try:
                reply = slave["socket"].recv( 4096 )
                reply = gurulhutils.unwrap_message( reply )
                if( reply["rtype"] == "warning" ):
                    pass
                else:
                    replies.put( reply )
            except BlockingIOError:
                pass
            except Exception as e:
                if( debug ): print( "Error in botnet_handler.py, listen_loop: ", e, flush=True )
                slave["socket"].close()
                slave_list.remove( slave )


def daemonize( read_pipe, write_pipe, queries, replies, keys ):
    global server_socket
    global slave_list
    global module_list

    slave_list = []
    module_list = []

    status = server_setup()
    gurulhutils.status_check( status, write_pipe )

    server_thread = threading.Thread( target= server_loop, daemon = True )
    router_thread = threading.Thread( target= route_loop, args = [ write_pipe, queries ], daemon = True )
    listen_thread = threading.Thread( target= listen_loop, args = [ replies ], daemon = True )

    server_thread.start()
    router_thread.start()
    listen_thread.start()

    while( True ):
        gurulhutils.sleep( 1 )
        pass
