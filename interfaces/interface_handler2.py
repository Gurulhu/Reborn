import queue
import threading
import gurulhutils

class InterfaceHandler(object):
    """docstring for ."""
    def __init__(self, keys, parent, queries, replies, system):
        self.name = "Interface Handler"
        self.parent = parent
        self.keys = keys
        self.queries = queries
        self.replies = replies
        self.system = system
        self.alive = False
        self.safe = False
        self.loop = threading.Thread( target=self.monitor, args=() )
        self.interface_dict = {} #info and imports
        self.Interfaces = {} #actual instances

    def start(self):
        print( "Starting " + self.name + ".", flush=True)
        self.alive = True
        self.refresh_list()
        for interface in self.interface_dict.keys():
            self.instanciate( interface )
        self.alive = True
        self.loop.start()
        print( self.name + " up!", flush=True)

    def refresh_list(self):
        print( "Refreshing Interface list.", flush=True)
        status, database = gurulhutils.db_init( self.keys["Database"] )
        if status:
            self.interface_dict = gurulhutils.import_modules( database, "interfacedb" )

    def instanciate(self, name):
        if name in self.interface_dict.keys():
            print( "Creating " + name + ".", flush=True)
            try:
                self.Interfaces.update( { name: self.interface_dict[name]["module"].Interface( self.keys[name],
                                                                                                self.name,
                                                                                                self.queries,
                                                                                                self.replies,
                                                                                                self.system ) } )
                self.Interfaces[name].start()
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )

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
        print( self.name + " is shutting down.", flush=True)
        for interface in self.Interfaces.keys():
            self.system.put( {"topic":[self.Interfaces[interface].name],
                            "code":-1,
                            "ttl": 10,
                            "content": self.name + " is shutting down."})

        while( False in [ self.Interfaces[interface].safe for interface in self.Interfaces.keys() ] ):
            print( [ self.Interfaces[interface].name + " = " + str( self.Interfaces[interface].safe ) for interface in self.Interfaces.keys() ] )
            gurulhutils.sleep(2500)

        self.safe = True
        self.system.put( {"topic":[self.parent, self.name],
                        "code":-1,
                        "ttl": 10,
                        "content": self.name + " has shut down."})
