import time
import smtplib
import threading
import gurulhutils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

debug = True

def init( token ):
    global server
    global addr

    try:
        server = smtplib.SMTP( token[0], int( token[1] ) )
        server.starttls()
        server.login( token[2], token[3] )
        addr = token[2]
        return "ok"
    except Exception as e:
        if( debug ): print( "Error in email_interface.py, init(): ", e, flush=True )
        return "fail"

def get_queries():
    pass

def digest_queries( queue ):
    pass

def get_replies( read_pipe ):
    global replies

    while( True ):
        gurulhutils.sleep( 1 )
        read_pipe.poll()
        reply = read_pipe.recv()
        replies.append( reply )

def digest_replies( ):
    global replies
    global server
    global addr

    while True:
        gurulhutils.sleep( 1 )
        for reply in replies:
            try:
                msg = MIMEMultipart()
                msg["From"] = addr
                msg["To"] = reply["to"]
                msg["Subject"] = "Re:" + reply["qcontent"]
                msg.attach( MIMEText( reply["rcontent"], "plain" ) )

                server.sendmail( addr, reply["to"], msg.as_string() )

                replies.remove( reply )
            except Exception as e:
                if( debug ): print( "Error in email_interface.py, digest_replies(): ", e, flush=True )


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
            if( debug ): print( "Error in email_interface.py, main(): ", e, flush=True )
            status = "down"
