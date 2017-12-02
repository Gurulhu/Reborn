from bs4 import BeautifulSoup
import requests
import time
import multiprocessing as mp
import re

debug = True

def init( keys ):
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
            reply += "    --//--    \n"

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

        containers = soup.find_all( class_="cardComponentContainer" )

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
            rows = container.find_all( class_="row" )
            for row in rows:
                label, value = row.text.replace("\n", "").replace("\r", "").replace( "  ", "" ).split( ":", 1 )
                if label in ["Mana Cost", "Other Sets", "All Sets"]:
                    symbols = row.find_all( "img" )
                    value = str( [ symbol["alt"] for symbol in symbols ] )
                    for c in ["[","]","'","'",]:
                        value = value.replace( c, "" )

                if label in ["Card Text"]:
                    lines = row.find_all( class_="cardtextbox" )
                    value = ""
                    for line in lines:
                        text = str( line )
                        if text.find( "<img" ) >= 0:
                            text = re.sub( "(<.*?alt=\")(.*?)(\".*?>)", "\\2", text )
                            text = re.sub( "<.*?>", "", text )
                        else:
                            text = line.text
                        value = value + text + "\n"
                    value = value[:-1]

                side.update( { label : value } )
            card.append( side )

        reply = ""
        for side in card:
            reply += "    --//--    \n"
            for key in side.keys():
                reply += str( key ) + ":\n" + str( side[ key ] ) + "\n\n"
            reply += "    --//--    \n\n"

        return "text", reply
    except Exception as e:
        if( debug ): print( "Error in mtguru.py, card_search: ", e, flush=True )
        return "text", "Sorry, something went wrong."

def create_list():
    url = ["http://gatherer.wizards.com/Pages/Search/Default.aspx?page=", "&output=compact&format=[%22Standard%22]"]
    page = -1
    cards = {}

    while True:
        page += 1
        r = requests.get( url[0] + str( page ) + url[1] )
        soup = BeautifulSoup( r.text, "html.parser" )
        names = soup.find_all( class_=["name top", "printings top"] )
        if names[0].text.replace("\n","") in cards.keys():
            break
        for i in range( 0, len( names ), 2 ):
            cards.update( { names[i].text.replace("\n", "") : [ ed["alt"] for ed in names[i+1].find_all("img") ] } )

    for land in ["Plains", "Island", "Swamp", "Mountain", "Forest"]:
        del( cards[land] )

    return cards

def full_search( name ):
    try:
        card = []
        print( name )
        #Ligamagic
        query_string = "https://www.ligamagic.com.br/?view=cards/card&card=" + name.replace(" ", "+")
        #print( query_string )
        r = requests.get( query_string )
        soup = BeautifulSoup( r.text, "html.parser" )

        try:
            exp = soup.find( class_="edicoes" ).find_all("img")
            exp = [ ed["title"] for ed in exp ]
        except:
            return card

        for i in range( len( exp ) ):
            if exp[i].find( "/" ) > 0: #Fixing portuguese names
                exp[i] = exp[i].split(" / ")[1]

            lowLiga = soup.find( id="omoPrimeMenor_" + str( i ) ).text
            lowLiga = float( lowLiga.replace(",",".").replace(" ","").replace("-","-1.0").replace("R$","") )
            meanLiga = soup.find( id="omoPrimeMedio_" + str( i ) ).text
            meanLiga = float( meanLiga.replace(",",".").replace(" ","").replace("-","-1.0").replace("R$","") )
            highLiga = soup.find( id="omoPrimeMaior_" + str( i ) ).text
            highLiga = float( highLiga.replace(",",".").replace(" ","").replace("-","-1.0").replace("R$","") )

            card.append( {
                "nome"          : name,
                "edicao"        : exp[i],
                "menorLiga"     : lowLiga,
                "medioLiga"     : meanLiga,
                "maiorLiga"     : highLiga,
            } )


        for i in range( len( exp ) ):
            #MTG Card Market (EU)
            lowMarket = -1.0
            meanMarket = -1.0
            try:
                query_string = "https://www.cardmarket.com/en/Magic/Products/Singles/"
                query_string += exp[i].replace("Masterpiece Series: ", "").replace(" ", "+") + "/" + name.replace(" ", "+")

                r = requests.get( query_string )
                soup = BeautifulSoup( r.text, "html.parser" )

                table = soup.find( class_="availTable" ).find_all("tr")

                for line in table :
                    if line.text.find( "From (EX+)" ) >= 0:
                        lowMarket = line.text.split(":")[1]
                        lowMarket = float( lowMarket.replace(",",".").replace(" ","").replace("€","") )
                    if line.text.find( "Price Trend" ) >= 0:
                        meanMarket = line.text.split(":")[1]
                        meanMarket = float( meanMarket.replace(",",".").replace(" ","").replace("€","") )

            except Exception as e:
                print( query_string )
                print( e )

            #MTGGoldFish (US)
            meanFish = -1.0
            try:
                query_string = "https://www.mtggoldfish.com/price/"
                query_string += exp[i].replace("Masterpiece Series: ", "").replace(":", "").replace(",", "").replace("'", "").replace(" ", "+") + "/" + name.replace(",", "").replace("'", "").replace(" ", "+") + "#paper"

                r = requests.get( query_string )
                soup = BeautifulSoup( r.text, "html.parser" )

                meanFish = soup.find( class_="price-box paper" ).find( class_="price-box-price" ).text

                meanFish = float( meanFish )

            except Exception as e:
                print( query_string )
                print( e )


            card[i].update( {
                "menorMarket"   : lowMarket,
                "medioMarket"   : meanMarket,
                "medioFish"     : meanFish
            })

        return card
    except:
        print( "ERRO: ", name )
        return []


def scrap():
    print( "Recuperando cartas no T2." )
    perf = time.time()
    card_list = create_list()
    perf = time.time() - perf
    print( "Terminado em " + str( perf ) + " (segundos?)." )
    sheet = {}

    data = time.localtime()
    data = str( data.tm_mday ) + "-" + str( data.tm_mon ) + "-" + str( data.tm_year )

    print( "Recuperando cambio do dia." )
    query = "http://g1.globo.com/economia/mercados/cotacoes/moedas/"
    r = requests.get( query )
    soup = BeautifulSoup( r.text, "html.parser" )

    dolar = soup.find( class_="even first" ).find_all( "td" )[1].text
    dolar = float( dolar.replace( ",", "." ) )

    euro = soup.find( class_="odd" ).find_all( "td" )[1].text
    euro = float( euro.replace( ",", "." ) )

    cards = []

    print( "Processando cartas." )
    perf = time.time()

    with mp.Pool( ) as pool:
        res = pool.map_async( full_search, (card for card in card_list) )
        res = res.get()
        for card in res:
            cards.extend( card )

    for card in cards:
        card.update( {
            "data"              : data,
            "menorMarketReal"   : card["menorMarket"] * euro,
            "medioMarketReal"   : card["medioMarket"] * euro,
            "medioFishReal"     : card["medioFish"] * dolar,
        } )

    perf = time.time() - perf
    print( "Terminado em " + str( perf ) + " (segundos?)." )
    return cards

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
    except ( KeyError, IndexError ):
        reply_type, reply = help()

    rinterface = query["qinterface"]
    rinterface["specific"].update( { "type" : "text" } )
    query.update( { "rinterface" : { rinterface["name"] : rinterface }, "to": query["from"], "rcontent" : reply } )

    return query
