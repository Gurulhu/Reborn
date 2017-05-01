import threading
import time
import telepot
import gurulhutils

debug = True

def init( token ):
    global bot

    try:
        bot = telepot.Bot( token[0] )
        return "ok"
    except Exception as e:
        if( debug ): print( "Error in telegram_interface.py, init(): ", e, flush=True )
        return "fail"

def fix_edited_message( query ):
    #fix for edited messages:
    try:
        query.update( { u'message': query["edited_message"] } )
    except:
        pass

def get_queries():
    global queries

    last_read = 0

    while( True ):
        gurulhutils.sleep( 1 )
        try:
            updates = bot.getUpdates( last_read, timeout=5 )

            for query in updates:
                try:
                    fix_edited_message( query )
                    content_type, chat_type, chat_id = telepot.glance( query["message"] )
                    queries.append( { u'qtype': content_type, u'qinterface': u'Telegram', u'qcontent': query['message'][content_type], u'from': chat_id, u'extra': query} )
                except:
                    query_id, chat_id, query_string = telepot.glance( query["inline_query"], flavor="inline_query" )
                    queries.append( { u'qtype': "inline_query", u'qinterface': u'Telegram', u'qcontent': query_string, u'from': chat_id, u'id': query_id, u'extra': query} )
                last_read = int( query["update_id"] ) + 1
        except( telepot.exception.BadHTTPResponse ):
            if( debug ): print( "Error in telegram_interface.py, get_queries(): Bad HTTP Response", flush=True )
        except Exception as e:
            if( debug ): print( "Error in telegram_interface.py, get_queries(): ", e, flush=True )

def digest_queries( queue ):
    global queries

    while( True ):
        gurulhutils.sleep( 1 )
        for query in queries:
            queue.put( query )
            queries.remove( query )

def get_replies( read_pipe ):
    global replies

    while( True ):
        gurulhutils.sleep( 1 )
        read_pipe.poll()
        reply = read_pipe.recv()
        replies.append( reply )

def digest_replies( ):
    global replies

    response_dictionary = {
        "text": bot.sendMessage,
        "photo": bot.sendPhoto,
        "audio": bot.sendAudio,
        "file": bot.sendDocument,
        "video": bot.sendVideo,
        "voice": bot.sendVoice,
        "location": bot.sendLocation,
        "contact": bot.sendContact,
    }

    while( True ):
        gurulhutils.sleep( 1 )
        for reply in replies:
            print( reply, flush=True )
            try:
                if( reply["qtype"] == "inline_query" ):
                    bot.answerInlineQuery( inline_query_id=reply["id"], results=[ { "type" : "article", "id" : reply["id"], "title" : reply["qcontent"], "description" : reply["rcontent"], "message_text" : reply["rcontent"] } ] )
                elif( "keyboard" in reply.keys() ):
                    response_dictionary[ reply['rtype'] ]( reply['from'], reply['rcontent'], reply_markup=reply["keyboard"] )
                else:
                    response_dictionary[ reply['rtype'] ]( reply['from'], reply['rcontent'] )
                replies.remove( reply )
            except Exception as e:
                if( debug ): print( "Error in telegram_interface.py, digest_replies(): ", e, flush=True )

def daemonize( read_pipe, write_pipe, queue, key ):
    global queries
    global replies

    queries = []
    replies = []
    status = init( key )
    gurulhutils.status_check( status, write_pipe )

    thread_dictionary = {
        "get_queries" : [ get_queries, (), True, "get_queries" ],
        "digest_queries" : [ digest_queries, [ queue ], True, "digest_queries" ],
        "get_replies" : [ get_replies, [ read_pipe ], True, "get_replies" ],
        "digest_replies" : [ digest_replies, (), True, "digest_replies" ]
    }

    thread_list = []

    for thread in thread_dictionary.values():
        thread_list.append( threading.Thread( target = thread[0], args = thread[1], daemon = thread[2], name = thread[3] ) )

    for thread in thread_list:
        thread.start()

    while( status != "down" ):
        gurulhutils.sleep( 1 )
        try:
            for thread in thread_list:
                if( not thread.is_alive() ):
                    thread = threading.Thread( target = thread_dictionary[ thread.name ][0], args = thread_dictionary[ thread.name ][1], daemon = thread_dictionary[ thread.name ][2], name = thread_dictionary[ thread.name ][3] )

        except Exception as e:
            if( debug ): print( "Error in telegram_interface.py, main(): ", e, flush=True )
            status = "down"
