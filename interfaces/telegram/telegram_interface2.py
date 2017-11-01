import threading
import telepot
import queue
import time

class Interface(object):
    """docstring for ."""
    def __init__(self, key, parent, queries, replies, system):
        self.bot = telepot.Bot( key[0] )
        self.name = "Telegram Interface"
        self.parent = parent
        self.queries = queries
        self.replies = replies
        self.system = system
        self.alive = False
        self.safe = False
        self.query_loop = threading.Thread( target=self.digest_queries, args=() )
        self.reply_loop = threading.Thread( target=self.digest_replies, args=() )
        self.monitor_loop = threading.Thread( target=self.monitor, args=() )

    def start(self):
        print( "Starting " + self.name + ".", flush=True)
        try:
            self.alive = True
            self.query_loop.start()
            self.reply_loop.start()
            self.monitor_loop.start()
            print( self.name + " up!", flush=True)
            return "ok"
        except:
            print( self.name + " failed.", flush=True)
            return "failed"

    def digest_queries(self):
        last_read = 0

        while self.alive:
            try:
                updates = self.bot.getUpdates( last_read, timeout=5 )
                for query in updates:
                    if "edited_message" in query.keys():
                        query.update( { "message": query["edited_message"] } )
                    content_type, chat_type, chat_id = telepot.glance( query["message"] )
                    self.queries.put( {"qinterface" :
                                        {
                                            "name"      : "Telegram",
                                            "specific"  : { "type": content_type }
                                        },
                                    "qcontent": query["message"][content_type],
                                    "from" : chat_id })
                    last_read = int( query["update_id"] ) + 1
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )


    def digest_replies(self):
        response_dictionary = {
            "text": self.bot.sendMessage,
            "photo": self.bot.sendPhoto,
            "audio": self.bot.sendAudio,
            "file": self.bot.sendDocument,
            "video": self.bot.sendVideo,
            "voice": self.bot.sendVoice,
            "location": self.bot.sendLocation,
            "contact": self.bot.sendContact,
        }

        while self.alive:
            try:
                reply = self.replies.get(True, 1)
                if "Telegram" in reply["rinterface"].keys():
                    response_dictionary[ reply["rinterface"]["Telegram"]["specific"]["type"] ]( reply['to'], reply['rcontent'] )
                else:
                    self.replies.put(reply)

            except queue.Empty:
                pass
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )

    def monitor(self):
        while self.alive:
            try:
                sysmsg = self.system.get(True, 1)
                if self.name in sysmsg["topic"]:
                    print( sysmsg["content"] )
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
        print( self.name +" is shutting down.", flush=True)
        self.query_loop.join()
        self.reply_loop.join()
        self.safe = True
        self.system.put( {"topic":[self.parent, self.name],
                        "code":-1,
                        "ttl": 10,
                        "content":"Telegram Interface has shut down."})
