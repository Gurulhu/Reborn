import queue
import threading
import gurulhutils

class InterfaceHandler(object):
    """docstring for ."""
    def __init__(self, keys, queries, replies, system):
        self.name = "Interface Handler"
        self.keys = keys
        self.queries = queries
        self.replies = replies
        self.system = system
        self.loop = threading.Thread( target=self.monitor, args=() )
        self.interface_dict = {} #info and imports
        self.interfaces = {} #actual instances
        self.alive = False

    def start(self):
        print( "Starting Interface Handler.", flush=True)
        self.alive = True
        self.refresh_list()
        for interface in self.interface_dict.keys():
            self.instanciate( interface )
        self.alive = True
        self.loop.start()
        print( "Interface Handler up!", flush=True)

    def refresh_list(self):
        print( "Refreshing Interface list.", flush=True)
        status, database = gurulhutils.db_init( self.keys["Database"] )
        if status:
            self.interface_dict = gurulhutils.import_modules( database, "interfacedb" )
            return "ok"
        else:
            return "failed"

    def instanciate(self, name):
        if name in self.interface_dict.keys():
            print( "Creating " + name + ".", flush=True)
            try:
                self.interfaces.update( { name:self.interface_dict[name]["module"].Interface( self.keys[name], self.queries, self.replies, self.system ) } )
                self.interfaces[name].start()
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )

    def monitor(self):
        while self.alive:
            try:
                sysmsg = self.system.get(True, 1)
                if "interface" in sysmsg["topic"]:
                    print( sysmsg["content"] )
                    if sysmsg["code"] == -1:
                        self.kill()
                else:
                    self.system.put( sysmsg )

            except queue.Empty:
                pass
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )

            if self.alive is False:
                self.system.put( {"topic":["main", "interface"],
                                "code":-1,
                                "ttl": 10,
                                "content":self.name + " has stopped working."})

    def kill(self):
        self.alive = False

        self.system.put( {"topic":["interface"],
                        "code":-1,
                        "ttl": 10,
                        "content":"Interface Handler has shut down."})
        #fix
