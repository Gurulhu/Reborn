import os
import multiprocessing

import gurulhutils
import interfaces.interface_handler2 as interface_handler
import botnet.botnet_handler2 as botnet_handler


class Bot( object ):

    def __init__(self):
        self.name = "Main"
        self.alive = True
        self.safe = False
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
        self.InterfaceHandler = interface_handler.InterfaceHandler( self.keys,
                                                                    self.name,
                                                                    self.queries,
                                                                    self.replies,
                                                                    self.system )
        return self.InterfaceHandler.start()

    def botnet_handler_create(self):
        print( "Creating Botnet Handler.", flush=True)
        self.BotnetHandler = botnet_handler.BotnetHandler( self.keys,
                                                                    self.name,
                                                                    self.queries,
                                                                    self.replies,
                                                                    self.system )
        return self.BotnetHandler.start()

    def start(self):
        try:
            print( "Starting Bot.", flush=True)
            self.keys_create()
            while self.botnet_handler_create() < 0 :
                gurulhutils.sleep(5000) #Most likely open sockets waiting to be flushed
                print( "Retrying Botnet Handler\n", flush = True )
            while self.interface_handler_create() < 0 :
                gurulhutils.sleep(1000)
                print( "Retrying Interface Handler\n", flush = True )

            print( "Bot up!", flush=True)
        except:
            self.cleanup()

    def cleanup(self):
        self.system.put( {"topic":[self.InterfaceHandler.name], "content":"Bot is shutting down.", "code":-1, "ttl":10} )
        self.system.put( {"topic":[self.BotnetHandler.name], "content":"Bot is shutting down.", "code":-1, "ttl":10} )

        while( False in [ self.InterfaceHandler.safe, self.BotnetHandler.safe ]):
            print( "Interface:", self.InterfaceHandler.safe )
            print( "Botnet:", self.BotnetHandler.safe )
            gurulhutils.sleep(2500)

        self.alive = False
        self.safe = True


if __name__ == "__main__":
    main = Bot()
    main.start()
    try:
        input()
    except:
        pass
    main.cleanup()
