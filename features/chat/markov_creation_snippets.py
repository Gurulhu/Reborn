f = open("taylor.txt")
lines = f.read().split("\n")
f.close()
words = []
for i in lines:
     words.extend( i.split(" ") )

words = pd.Dataframe( words )
words = words[0].unique()

db = {}
for word in words:
     db.update( { word : { "_word" : word } } )

db.update( {"_begin" : {"_word" : "_begin" } } )

for i in lines:
     line = i.split(" ")
     try:
         n = db["_begin"][line[0]]
     except:
         n = 0
     db["_begin"].update( { line[0] : n + 1 } )
     for j in range( 1, len( line ) - 1 ):
         try:
             n = db[line[j-1]][line[j]]
         except:
             n = 0
         db[line[j-1]].update( { line[j] : n + 1 } )
     l = len( line ) - 1
     try:
         n = db[ line( l ) ]["_end"]
     except:
         n = 0
     db[ line[ l ]].update( {"_end" : n + 1} )
     print( line, line[l] )


result = collection.insert_many( [db[i] for i in db.keys() ] )
