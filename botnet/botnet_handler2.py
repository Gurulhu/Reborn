import queue
import socket
import threading
import gurulhutils

class BotnetHandler( object ):

    def __init__( self, keys, parent, queries, replies, system ):
        self.name = "Botnet Handler"
        self.keys = keys
        self.parent = parent
        self.queries = queries
        self.replies = replies
        self.system = system
        self.alive = False
        self.safe = False
        self.Slaves = {}
        self.slave_hasher = 0
        self.modules = []
        self.calls = {}
        self.server_loop = threading.Thread( target=self.server, args=() )
        self.route_loop = threading.Thread( target=self.route, args=() )
        self.listen_loop = threading.Thread( target=self.listen, args=() )
        self.monitor_loop = threading.Thread( target=self.monitor, args=() )


    def start(self):
        print( "Starting " + self.name + ".", flush=True)
        self.alive = True
        self.server_setup()
        self.server_loop.start()
        self.route_loop.start()
        self.listen_loop.start()
        self.monitor_loop.start()
        if self.alive:
            print( self.name + " up!", flush=True)
            return 0
        else:
            print( self.name + " has failed!", flush=True)
            self.cleanup()
            return -1

    def refresh_module_list( self ):
        print( "Refreshing Calls list.", flush=True)
        status, database = gurulhutils.db_init( self.keys["Database"] )
        db = database.get_collection( "moduledb" )

        modules = []
        calls = {}

        cursor = db.find()
        for i in range( 0, cursor.count() ): #creates a two-way dic to translate modules into calls.
            calls.update( { cursor[i]["call"] : cursor[i]["name"] } )
            modules.append( cursor[i]["name"] )
        self.calls = calls
        self.modules = modules

    def server_setup( self ):
        try:
            server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            server.bind( ( "0.0.0.0", 13031 ) )
            server.listen( 80 )
            server.setblocking( False )
            self.socket = server

        except Exception as e:
            print( "Error in " + self.name + ":", e, flush=True )
            self.alive = False

    def handshake_connect( self, slave ):
        try:
            slave["socket"].settimeout(10.0)
            if gurulhutils.socket_recv( slave["socket"] ) == "dig":
                gurulhutils.socket_send( slave["socket"], "dig joy" )
            if gurulhutils.socket_recv( slave["socket"] ) == "dig joy popoy":
                gurulhutils.socket_send( slave["socket"], "Vem brincar comigo")

            info = gurulhutils.socket_recv( slave["socket"] )
            slave["socket"].setblocking( False )
            if info["hash"] == 0: #arrumar
                slave.update( { "hash" : info["hash"], "modules" : info["modules"] } )
                self.Slaves.update( { self.slave_hasher : slave } )
                self.slave_hasher += 1
                for module in slave["modules"]:
                    if module not in self.modules:
                        self.refresh_module_list()

        except BlockingIOError:
            pass
        except Exception as e:
            slave["socket"].close()
            print( "Error in " + self.name + ":", e, flush=True )

    def server( self ):
        while self.alive:
            try:
                sock, addr = self.socket.accept()
                slave = { "socket" : sock, "address" : addr }
                connect = threading.Thread( target=self.handshake_connect, kwargs={ "slave" : slave } )
                connect.start()

            except BlockingIOError:
                pass
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )

    def route( self ):
        while self.alive:
            try:
                query = self.queries.get(True, 1)
                if type( query["qcontent"] ) == str:
                    try:
                        module = self.calls[ query["qcontent"].split(" ")[0] ]
                    except:
                        module = self.calls[ "chat" ]

                    query.update( { "module" : module } )
                    keys = list( self.Slaves.keys() )
                    for slave in keys:
                        if module in self.Slaves[slave]["modules"]:
                            print( "Routing to " + str( self.Slaves[slave]["address"] ), flush=True )
                            gurulhutils.socket_send( self.Slaves[slave]["socket"], query )

            except queue.Empty:
                pass


    def listen(self):
        while self.alive:
            bad_slaves = []

            keys = list( self.Slaves.keys() )
            for slave in keys:
                try:
                    data = gurulhutils.socket_recv( self.Slaves[slave]["socket"] )
                    self.replies.put( data )
                except BlockingIOError:
                    pass
                except Exception as e:
                    bad_slaves.append( slave )

            if len( bad_slaves ) > 0:
                self.kill_slaves( bad_slaves )

    def kill_slaves( self, bad_slaves ):
        self.system.put( {"topic":[self.name],
                        "code":1,
                        "ttl": 3,
                        "content": str( len( bad_slaves ) ) + " slaves have failed and got killed.\n" + str( bad_slaves ) } )

        for slave in bad_slaves:
            del( self.Slaves[ slave ] )

    def monitor(self):
        while self.alive:
            try:
                sysmsg = self.system.get(True, 1)
                if self.name in sysmsg["topic"]:
                    print( self.name + " sysmsg:", sysmsg["content"] )
                    if sysmsg["code"] == -1:
                        self.alive = False
                else:
                    self.system.put( sysmsg )

            except queue.Empty:
                pass
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )

        self.cleanup()

    def cleanup(self):
        keys = list( self.Slaves.keys() )
        for slave in keys:
            #self.Slaves[slave].socket.close()
            pass

        try:
            self.socket.close()
        except Exception as e:
                        print( "Error in " + self.name + ":", e, flush=True )

        self.server_loop.join()
        self.route_loop.join()
        self.listen_loop.join()

        self.safe = True
        self.system.put( {"topic":[self.parent, self.name],
                        "code":-1,
                        "ttl": 10,
                        "content": self.name + " has shut down."})
