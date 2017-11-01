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


    def start(self):
        
