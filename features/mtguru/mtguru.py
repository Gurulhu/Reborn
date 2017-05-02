from bs4 import BeautifulSoup
import requests

debug = True

def init():
    return "ok"

def opt_check( token ):
    try:
        opt = None
        if( str( token[0] ).find("-") == 0 ):
            opt = str( token[0] )
            token = token[1:]
        return token, opt
    except Exception as e:
        if( debug ): print( "Error in mtguru.py, opt_check: ", e, flush=True )
        return token, None

def price_search( token ):
    try:
        token, opt = opt_check( token )

        if( opt ):
            if( opt == "-f" ):
                query_string = "https://www.ligamagic.com.br/?view=cards%2Fsearch&card="
        else:
            query_string = "https://www.ligamagic.com.br/?view=cards/card&card="

        for word in token:
            query_string += "+" + str( word )

        r = requests.get( query_string )

        soup = BeautifulSoup( r.text, "html.parser" )

        card_name = soup.find("p", class_="subtitulo-card")

        if( card_name is None ):
            card_name = soup.find("h3", class_="titulo-card b")

        if( card_name is None ):
            card_list = soup.find_all( class_=["pointer", "pointer zebra"] )
            if( len( card_list ) > 0 ):
                reply = "I found these, but I'm unsure which to choose:\n\n"
                dic = []
                for card in card_list:
                    name = card["onclick"][10:-3]
                    if( name not in dic ):
                        dic.append( name )
                        reply += name + "\n"
                        reply += "\n    --//--    \n\n"

                return "text", reply
            else:
                return "text", "Sorry, couldn't find the card you wanted it."

        expansion = soup.find( "ul", class_="edicoes" )
        lines = expansion.find_all("li")

        prices = []
        for i in range( len( lines ) ):
            exp = lines[i].contents[0].contents[0]["title"]
            low = soup.find( id="omoPrimeMenor_" + str( i ) ).text.strip()
            med = soup.find( id="omoPrimeMedio_" + str( i ) ).text.strip()
            hig = soup.find( id="omoPrimeMaior_" + str( i ) ).text.strip()
            prices.append( { "Expansion:" : exp, "Lowest:" : low, "Medium:": med, "Highest:": hig } )

        reply = "    --//--    \n"
        reply += "-> Card Name: \n" + str( card_name.text ) + "\n\n"
        for price in prices:
            reply += "-> Expansion: " + price["Expansion:"] + "\n"
            reply += "Lowest: " + price["Lowest:"] + "\n"
            reply += "Medium: " + price["Medium:"] + "\n"
            reply += "Highest: " + price["Highest:"] + "\n\n"
            reply += "    --//--    \n\n"

        return "text", reply

    except Exception as e:
        if( debug ): print( "Error in mtguru.py, price_search: ", e, flush=True )
        return "text", "Sorry, something went wrong."


def string_strip( obj ):
    try:
        if( obj.string ):
            return obj.string.strip()
        else:
            result_string = ""
            for string in obj.strings:
                if( string.strip() != ""):
                    result_string += string.strip() + "\n"
            return result_string
    except Exception as e:
        if( debug ): print( "Error in mtguru.py, string_strip: ", e, flush=True )
        return obj

def card_search( token ):
    try:
        token, opt = opt_check( token )

        query = ""
        for word in token:
            query += "+[" + str( word ) + "]"

        if( opt ):
            if( opt == "-tp"):
                query_string = "http://gatherer.wizards.com/Pages/Search/Default.aspx?type=" + query + "||subtype=" + query
            if( opt == "-tx" ):
                query_string = "http://gatherer.wizards.com/Pages/Search/Default.aspx?text=" + query
        else:
            query_string = "http://gatherer.wizards.com/Pages/Search/Default.aspx?name=" + query

        r = requests.get( query_string )

        soup = BeautifulSoup( r.text, "html.parser" )

        containers = soup.find_all( class_='cardComponentContainer')

        if( len( containers ) == 0 ):
            if( soup.find( class_="cardList" )): #Winded up on the search list
                card_list = soup.find_all( class_="cardInfo")
                reply = "I found these, but I'm unsure which to choose:\n\n"
                for card in card_list:
                    reply += string_strip( card.find( class_="cardTitle" ) )
                    reply += "\n    --//--    \n\n"

                return "text", reply
            else:
                return "text", "Sorry, couldn't find the card you wanted it."

        card = []

        for container in containers:
            side = {}
            labels = container.find_all( class_="label" )
            values = container.find_all( class_="value" )
            for i in range( 1, len( labels ) ):
                label = string_strip( labels[i] )
                value = string_strip( values[i] )
                side.update( { label : value } )

            card.append( side )

        reply = ""
        for side in card:
            reply += "    --//--    \n"
            for key in side.keys():
                if( key not in [ "Mana Cost:", "All Sets:" ] ):
                    reply += "-> " + str( key ) + "\n" + str( side[ key ] ) + "\n\n"

            reply += "    --//--    \n\n"

        return "text", reply
    except Exception as e:
        if( debug ): print( "Error in mtguru.py, card_search: ", e, flush=True )
        return "text", "Sorry, something went wrong."

def help():
    return "text", "Search for MTG Cards remotely! \n/mtg [opt] [card name]\n\nOpts:\n-st - Card Search [Text Only]\n-p - Price Search"

def reply( query ):
    print("MTG", flush=True)

    responses = {
        "-st" : card_search,
        "search" : card_search,
        "-p" : price_search,
        "price" : price_search
    }

    token = query["qcontent"].split()

    try:
        reply_type, reply = responses[token[1]]( token[2:] )
        return query["qinterface"], reply_type, reply
    except KeyError:
        reply_type, reply = help()
        return query["qinterface"], reply_type, reply
    except ( KeyError, IndexError ):
        reply_type, reply = help()
        return query["qinterface"], reply_type, reply

reply( { "qinterface" : "Telegram", "qcontent" : "/mtg -p Karma" } )
