import threading
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
        try:
            updates = bot.getUpdates( last_read )

            for query in updates:
                fix_edited_message( query )
                content_type, chat_type, chat_id = telepot.glance( query["message"] )
                queries.append( { u'qtype': content_type, u'qinterface': u'Telegram', u'qcontent': query['message'][content_type], u'from': chat_id, u'extra': query} )
                last_read = int( query["update_id"] ) + 1
        except Exception as e:
            if( debug ): print( "Error in telegram_interface.py, get_queries(): ", e, flush=True )

def digest_queries( queue ):
    global queries

    while( True ):
        for query in queries:
            queue.put( query )
            queries.remove( query )

def get_replies( read_pipe ):
    global replies

    while( True ):
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
        "contact": bot.sendContact
    }

    while( True ):
        for reply in replies:
            try:
                response_dictionary[ reply['rtype'] ]( reply['from'],reply['rcontent'], reply_markup=reply["keyboard"] )
            except Exception as e:
                response_dictionary[ reply['rtype'] ]( reply['from'],reply['rcontent'] )
            replies.remove( reply )


def daemonize( read_pipe, write_pipe, queue, key ):
    global queries
    global replies

    queries = []
    replies = []
    status = init( key )
    gurulhutils.status_check( status, write_pipe )

    thread_list = []
    thread_list.append( threading.Thread( target = get_queries, daemon = True ) )
    thread_list.append( threading.Thread( target = digest_queries, args = [ queue ], daemon = True ) )
    thread_list.append( threading.Thread( target = get_replies, args = [ read_pipe ], daemon = True ) )
    thread_list.append( threading.Thread( target = digest_replies, daemon = True ) )

    for thread in thread_list:
        thread.start()

    while( status != "down" ):
        try:
            for thread in thread_list:
                if( not thread.is_alive() ):
                    thread.run()

        except Exception as e:
            if( debug ): print( "Error in telegram_interface.py, main(): ", e, flush=True )
            status = "down"
