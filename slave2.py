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
        self.keys = {}

    def start( self ):
        self.alive = True
        if len( self.keys ) == 0:
            self.keys_create()
        if len( self.module_dict ) == 0:
            self.refresh_list()
            self.init_modules()
        self.handshake_connect()
        if self.alive:
            return self.main()

    def keys_create( self ):
        print( "Gathering keys.", flush=True)
        self.keys = {}
        for key in os.environ.keys():
            if key.find("key_") >= 0:
                args = os.environ[key].split(",")
                self.keys.update( {args[0]:args[1:]} )

    def refresh_list( self ):
        print( "Refreshing Modules list.", flush=True)
        self.module_dict = {}
        status, database = gurulhutils.db_init( self.keys["Database"] )
        if status:
            self.module_dict = gurulhutils.import_modules( database, "moduledb" )

    def init_modules( self ):
        print( "Initiating modules.", flush=True)
        for module in self.module_dict:
            self.module_dict[module]["module"].init( self.keys )

    def hash_itself( self ):
        return 0 #arrumar

    def handshake_connect( self ):
        print( "Connecting to Server.", flush=True)
        self.Server = None
        try:
            server_addr = ( socket.gethostbyname( self.keys["Server"][0] ), int( self.keys["Server"][1] ) )
            server = socket.create_connection( server_addr )
            gurulhutils.socket_send( server, "dig" )
            if gurulhutils.socket_recv( server ) == "dig joy":
                gurulhutils.socket_send( server, "dig joy popoy" )
            if gurulhutils.socket_recv( server ) == "Vem brincar comigo":
                info = { "hash" : self.hash_itself(), "modules" : list( self.module_dict.keys() ) }
                gurulhutils.socket_send( server, info )
                server.setblocking( False )
                self.Server = server
        except Exception as e:
            print( "Failed: ", e, flush=True )
            self.alive = False

    def main( self ):
        print( "Slave up!", flush=True )
        while self.alive:

            try:
                query = gurulhutils.socket_recv( self.Server )
                print( query )
                reply = self.module_dict[ query["module"] ]["module"].reply( query )
                gurulhutils.socket_send( self.Server, reply )

            except BlockingIOError:
                pass

            except JSONDecodeError or ConectionResetError:
                print( "Connection lost.", flush=True)
                self.Server.close()
                self.handshake_connect()

            except Exception as e:
                print( e, flush=True )
                print( e.with_traceback )

if __name__ == "__main__":
    slave = Slave()
    while not slave.safe:
        slave.start()
