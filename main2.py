import os
import multiprocessing

import gurulhutils
import interfaces.interface_handler2 as interface_handler


class Bot( object ):

    def __init__(self, args):
        self.queries = multiprocessing.Queue()
        self.replies = multiprocessing.Queue()
        self.system = multiprocessing.Queue()

    def keys_create(self):
        print( "Gathering keys.", flush=True)
        self.keys = {}
        for key in os.environ.keys():
            if key.find("key_") >= 0:
                args = os.environ[key].split(",")
                self.keys.update( {args[0]:args[1:]} )

    def interface_handler_create(self):
        print( "Creating Interface Handler.", flush=True)
        self.InterfaceHandler = interface_handler.InterfaceHandler( self.keys, self.queries, self.replies, self.system )
        self.InterfaceHandler.start()

    def start(self):
        print( "Starting Bot.", flush=True)
        self.keys_create()
        self.interface_handler_create()
        print( "Bot up!", flush=True)

    
