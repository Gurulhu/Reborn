import threading
import telepot
import queue
import time

class Interface(object):
    """docstring for ."""
    def __init__(self, key, queries, replies, system):
        self.bot = telepot.Bot( key[0] )
        self.name = "Telegram Interface"
        self.queries = queries
        self.replies = replies
        self.system = system
        self.alive = False
        self.query_loop = threading.Thread( target=self.digest_queries, args=() )
        self.reply_loop = threading.Thread( target=self.digest_replies, args=() )
        self.monitor_loop = threading.Thread( target=self.monitor, args=() )

    def start(self):
        try:
            self.alive = True
            self.query_loop.start()
            self.reply_loop.start()
            self.monitor_loop.start()
            return "ok"
        except:
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
                if "telegram" in sysmsg["topic"]:
                    print( sysmsg["content"] )
                    if sysmsg["code"] == -1:
                        self.kill()
                else:
                    self.system.put( sysmsg )

            except queue.Empty:
                pass
            except Exception as e:
                print( "Error in " + self.name + ":", e, flush=True )

    def kill(self):
        self.alive = False
        while ( self.query_loop.is_alive() or self.reply_loop.is_alive() ):
            time.sleep(1)
        self.system.put( {"topic":["interface", "telegram"],
                        "code":-1,
                        "ttl": 10,
                        "content":"Telegram Interface has shut down."})
