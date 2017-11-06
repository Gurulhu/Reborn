import os
import socket
import json
import gurulhutils

class Slave( object ):

    def __init__( self, args=None ):
        self.name = "Slave"
        self.alive = True
        self.safe = False
        self.module_dict = {}

    def start( self ):
        self.keys_create()
        self.refresh_list()
        self.handshake_connect()

    def keys_create( self ):
        print( "Gathering keys.", flush=True)
        self.keys = {}
        for key in os.environ.keys():
            if key.find("key_") >= 0:
                args = os.environ[key].split(",")
                self.keys.update( {args[0]:args[1:]} )

    def refresh_list( self ):
        print( "Refreshing Modules list.", flush=True)
        status, database = gurulhutils.db_init( self.keys["Database"] )
        if status:
            self.module_dict = gurulhutils.import_modules( database, "moduledb" )

    def hash_itself( self ):
        return 0

    def handshake_connect( self ):
        self.Server = None
        server_addr = ( socket.gethostbyname( self.keys["Server"][0] ), int( self.keys["Server"][1] ) )
        server = socket.create_connection( server_addr )
        gurulhutils.socket_send( server, "dig" )
        if gurulhutils.socket_recv( server ) == "dig joy":
            gurulhutils.socket_send( server, "dig joy popoy" )
        if gurulhutils.socket_recv( server ) == "Vem brincar comigo":
            info = { "hash" : self.hash_itself(), "modules" : list( self.module_dict.keys() ) }
            gurulhutils.socket_send( server, info )
            self.Server = server


if __name__ == "__main__":
    slave = Slave()
    slave.start()
    gurulhutils.sleep(100)
    gurulhutils.socket_send( slave.Server, "Olar" )
