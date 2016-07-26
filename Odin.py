#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Odin.py: Odin reads and writes shit.

 - Read a string or a file, compute the frequency of groups of words and update a SQLite database with the result.
 - Get a string, a chain of strings or a text, from a starting pattern. Based on frequency of apparition or randomly.

"""

import sys
import os
import re
import datetime
import random
import sqlite3

from collections import deque

__version__ = "0.4"
__author__  = "Marotte"
__licence__ = "GPL"
__status__  = "Experimental"

class Odin:

    def initLog(self, filename):
    
        self.Log = open(filename,"a")
        size = os.stat(filename).st_size
        self.Log.write("\n"+str(datetime.datetime.now())+":"+"initLog: "+filename+" ("+str(size)+" B)\n")

    def log(self, message):

        self.Log.write(str(datetime.datetime.now())+":"+message+"\n")
        print(message,file=sys.stderr)        

    def connectDB(self,filename):
        
        self.DBConnection = sqlite3.connect(filename)
        self.DBCursor = self.DBConnection.cursor()
        self.initDB()
        
    def initDB(self):

        
        self.DBCursor.execute("CREATE TABLE IF NOT EXISTS strings (string TEXT NOT NULL, freq INT, length INT, PRIMARY KEY(string))")
        self.DBCursor.execute("PRAGMA synchronous=0")
        self.DBConnection.commit()
        
        self.log("initDB: "+str(self.DBConnection))

    def __init__(self, name,\
                             STRING_MINWORDS     = 3,\
                             STRING_MAXWORDS     = 4,\
                             FETCH_BY            = 1024,\
                             # When encoutered the word is re-splited :
                             WORD_RESPLIT        = '[A-Za-zéà\)\]]+(\,\.|\!|\?)+[A-Za-zéà\(\]]',\
                             # Drop the following strings if they appear as single word. (don't remove the empty string…) :
                             WORD_DROP           = ('',)+(':',';','«','»','-','—','–','»,','=','+','*'),\
                             CHAIN_MINWORDS      = 2,\
                             CHAIN_END           = '(.*)([A-Za-zéà ]+)(\.|\!|\?)( |\.|\"*)$',\
                             LOAD_ORDER          = 'freq_desc',\
                             MAX_RESULTS         = -1,\
                             CONTEXT             = ''\
                ):

    
        self.strings       = {}
        self.new_strings   = {}
        self.up_strings    = {}
        self.fetchcount    = 0
        self.string        = ''
        self.chain         = ''

        self.STRING_MINWORDS     = STRING_MINWORDS
        self.STRING_MAXWORDS     = STRING_MAXWORDS
        self.FETCH_BY            = FETCH_BY
        self.WORD_RESPLIT        = WORD_RESPLIT
        self.WORD_DROP           = WORD_DROP
        self.LOAD_ORDER          = LOAD_ORDER
        self.MAX_RESULTS         = MAX_RESULTS
        self.CONTEXT             = CONTEXT
        self.CHAIN_MINWORDS      = CHAIN_MINWORDS
        self.CHAIN_END           = CHAIN_END

        self.initLog(name+".log")
        self.connectDB(name+".sqlite")
    
    def __del__(self):
    
        self.DBConnection.close()
        self.Log.close()

    def loadDB(self, limit = -1, order="freq_desc", max_results = -1, context = '', delete = True):
    
        self.fetchcount = 0
        
        if (max_results > -1):
            maxres = ' LIMIT '+str(max_results)
        else:
            maxres = ''
        
        if (context != ''):
            where = ' WHERE string LIKE "%'
            words = context.split(" ")
            where += '%" OR string LIKE "%'.join(words)
            where += '%" '
        else:
            where = ' '
        if (order == "freq_desc"):
            request = "SELECT * FROM strings"+where+"ORDER BY freq DESC"+maxres
            self.DBCursor.execute(request)
        elif (order == "random"):
            request = "SELECT * FROM strings"+where+"ORDER BY random()"+maxres
            self.DBCursor.execute(request)
        
        print('loadDB: '+request, file=sys.stderr)        
        if (limit == -1):
            results = self.DBCursor.fetchall()
            for result in results:
                self.strings[result[0]] = result[1]
        else:
            results = self.fetchDB(delete = delete)
            for result in results:
                self.strings[result[0]] = result[1]
        return True
   
    def fetchDB(self, delete = True):
        
        if (delete):
            self.strings = {}
          
        offset = random.randint(0,8)
        print("# FetchDB limit: "+str(self.FETCH_BY+offset),file=sys.stderr)
        results = self.DBCursor.fetchmany(self.FETCH_BY+offset) 
        self.fetchcount = self.fetchcount + self.FETCH_BY+offset  
        for result in results:
            self.strings[result[0]] = result[1]
        print("# Size of strings: "+str(len(self.strings)),file=sys.stderr)   
        return results
    
    def loadDBLike(self, search = '%', limit = -1, order="freq_desc", max_results = -1, context = '', delete = True):
        
        if (delete):
            self.strings = {}
        
        #~ print("loadDBLike: '"+search+"'", file=sys.stderr)
        self.fetchcount = 0
        context = self.CONTEXT
        search = search.replace('"',' ').replace('  ',' ')
        if (max_results > -1):
            maxres = ' LIMIT '+str(max_results)
        else:
            maxres = ''
        if (search == ''):
            search = '%'
        
        if (context != ''):
            where = ' WHERE string LIKE "'+search+' %" AND (string LIKE "% '
            words = context.split(" ")
            where += ' %" OR string LIKE "% '.join(words)
            where += ' %") '
        else:
            where = ' WHERE string LIKE "'+search+' %" '    
            
        
        if (order == "freq_desc"):
            request = "SELECT * FROM strings"+where+"ORDER BY freq DESC"+maxres
            print('loadDBLike: '+request, file=sys.stderr)
            self.DBCursor.execute(request)
        elif (order == "random"):
            request = "SELECT * FROM strings"+where+"ORDER BY random()"+maxres
            print('loadDBLike: '+request, file=sys.stderr)
            self.DBCursor.execute(request)
        
                
        if (limit == -1):
            results = self.DBCursor.fetchall()
            for result in results:
                self.strings[result[0]] = result[1]
                self.fetchcount = self.fetchcount + 1
        else:
            results = self.fetchDB(delete = delete)
            for result in results:
                self.strings[result[0]] = result[1]
        return True
        
    def clean(self):
        
        self.new_strings = {}
        self.up_strings = {}

    def syncDB(self):
        
        try:
            self.DBConnection.commit()
        except sqlite3.OperationalError as e:
            self.log("syncDB: Impossible to write to database ("+str(e)+"). Exiting…")
            sys.exit(1)
        self.clean()
    
    def updateDB(self):

        for string in self.new_strings:
            length = len(string.split(" "))
            freq = self.new_strings[string]
            self.DBCursor.execute("INSERT INTO strings (string, freq, length) VALUES (?,?,?)", (string, freq, length))
        for string in self.up_strings:
            freq = self.up_strings[string]
            self.DBCursor.execute("UPDATE strings SET freq=? WHERE string=?", (freq, string))
        self.syncDB()
        self.log("updateDB: Total changes: "+str(self.DBConnection.total_changes))  
        self.log("updateDB: Update OK. "+str(len(self.strings))+" strings.")
    
    def wordOK(self, word = ''):
        
        for s in self.WORD_DROP:
            if (word.strip() == s):
                return False
        return True           
        
    def sanitizeWord(self, word = ''):
    
        try:
            del self.strings[word]
            del self.new_strings[word]
            del self.up_strings[word]
        except KeyError:
            pass
        return re.split(self.WORD_RESPLIT, word)
      
    def readString(self, string = ''):     

        # Load all the strings we already know.
        self.loadDB(limit=-1, order = 'freq_desc')
        # Replace all characters that has nothing to deal with syntax in the provided string…
        string = string.replace("\N{NO-BREAK SPACE}","\N{SPACE}") \
                       .replace("\N{NARROW NO-BREAK SPACE}","\N{SPACE}") \
                       .replace("\N{CHARACTER TABULATION}","\N{SPACE}") \
                       .replace("\N{LINE TABULATION}","\N{SPACE}") \
                       .replace("\N{FORM FEED}","\N{SPACE}") \
                       .replace("\N{LINE FEED}","\N{SPACE}") \
                       .replace("\N{CARRIAGE RETURN}","\N{SPACE}")
        # Make an iterable from this
        words = string.split("\N{SPACE}")
        # and fixed length FIFO
        buf = deque(maxlen=self.STRING_MAXWORDS)
        # Iterate
        s = ''
        for word in words:
            # Test if word is OK and sanitize it (ex: 'foo.bar' → 'foo. bar')
            if (self.wordOK(word)):
                # The sanitizeWord method returns a list as it may split the word.
                # So we append every element of it to our buffer.
                # /!\ Yeah… all the element may not fit entierly in one buffer…
                # if so, it means we lose data… /!\

                for w in self.sanitizeWord(word):
                    for w2 in w.split():
                        buf.append(w2)               


            else:
                continue    
            # If the buffer is shorter than its max length or shorter than `words` then continue.
            if (len(buf) < min(buf.maxlen, len(words))):
                continue
            # We now have a buffer filled with acceptable words  
            # `sub` hold the current buffer
            # `s` hold the corresponding string (used as the key for the generated dict)
            sub = buf
            s = ''
            # Generate the strings for this buffer
            for w in sub:
                s = s + ' ' + w
                if (len(s.split()) < self.STRING_MINWORDS):
                    continue
                s = s.strip()    
                try:
                    # Update the dict (freq + 1)
                    self.strings[s] = self.strings[s] + 1
                    self.up_strings[s] = self.strings[s]
                except KeyError:
                     # If it fails it means it's a new string
                     self.new_strings[s] = 1
                     self.strings[s] = self.new_strings[s]
        # No more data to fill the buffer, but we need to process the remaining words it may still contain.         
        sub = s.split(" ")[1:]
        while (len(sub) > self.STRING_MINWORDS - 1):
            s = ' '.join(sub).strip()
            try:
                # Same shit as above but also we have to explicitely pop the word ourselves from the buffer each time.
                self.strings[s] = self.strings[s] + 1
                self.up_strings[s] = self.strings[s]
                sub = sub[1:]
            except KeyError:
                 self.new_strings[s] = 1
                 self.strings[s] = self.new_strings[s]
                 sub = sub[1:]             
       
        # Insert gathered strings to the database.
        self.log("readString: new: "+str(len(self.new_strings))+" update: "+str(len(self.up_strings)))
        self.updateDB()
        return {"strings": self.strings, "new_strings": self.new_strings, "up_strings": self.up_strings}

    def readFile(self,filename):
    
        if (filename != '-'):
            size = os.stat(filename).st_size
            self.log("readFile: '"+filename+"' ("+str(size)+" B)")
        else:
            self.log("readFile: Reading standard input…")    
        if not (filename == '-'):
            self.file = open(filename,mode="r",encoding="utf-8")
        else:
            self.file = sys.stdin
        data = self.file.read()
        self.readString(data)
        self.file.close()
        return True

    def getString(self,regexp = '(.*)', delete = True):
      
        search = re.compile(regexp)
        while (True):
            try:
                self.string = random.choice(list(self.strings.keys()))
                if (len(self.strings) == 0):
                    #~ print("len strings = 0:"+str(len(self.strings))+" "+self.string)
                    if (self.loadDB(self.FETCH_BY)):
                        continue                

                if (len(self.strings) < (self.FETCH_BY / 6)):
                    #~ print("len strings < self.FETCH_BY / 8: "+str(len(self.strings)))
                    self.fetchDB()
                    continue

                if (search.match(self.string)):  
                    #~ print(regexp+" → "+self.string+" OK "+str(len(self.strings))+" strings left.",file=sys.stderr)
                    return self.string
                    break
                else:
                    #~ print("#"+self.string,file=sys.stderr,end='')
                    if (delete):
                        del self.strings[self.string]
                    continue
            except (IndexError):

                    print(regexp+" → <!NO MATCH!> : "+str(len(self.strings))+" strings left.",file=sys.stderr)
                    self.string = ''
                    self.fetchDB()
                    return self.string

        return self.string
 
    def getChain(self,regexp = '(.*) ',minwords = 2, end = '(.*)([A-Za-zéà ]+)(\.|\!|\?)$'):

        self.loadDB(order = self.LOAD_ORDER, max_results = self.MAX_RESULTS, context = self.CONTEXT)
        self.string = self.getString(regexp, delete = True)
        self.chain = self.string
        hook = ' '.join(self.string.split(' ')[-2:])
        end = re.compile(self.CHAIN_END)
        
        while (hook != '' and len(self.chain) < 512 and len(self.strings) > 0):

            print("Last string: "+self.string,file=sys.stderr)
            #~ print("Hook: "+hook,file=sys.stderr)
            #~ print("Chain before: "+self.chain,file=sys.stderr)
            self.loadDBLike(search = hook, order = self.LOAD_ORDER, max_results = self.MAX_RESULTS, context = self.CONTEXT, delete = True)
            print("Size of strings: "+str(len(self.strings)), file=sys.stderr)
            
            

            
            try:
                self.string = random.choice(list(self.strings.keys()))
    
            except IndexError:
                self.fetchDB(delete = False)
                continue
            print("New string: "+self.string,file=sys.stderr)
            print("New part: "+str(self.string.split(" ")[len(hook.split(' ')):]), file=sys.stderr)
            if (len(self.strings) == 0):
                hook = hook[0]
                #~ self.fetchDB(delete = False)
                #~ self.loadDBLike(search = hook, order = self.LOAD_ORDER, max_results = self.MAX_RESULTS, context = self.CONTEXT, delete = True)
                continue
            if (end.match(self.string)):
                print("Match end: "+self.string, file=sys.stderr)
                self.chain = self.chain+' '+' '.join(self.string.split(" ")[len(hook.split(' ')):])
                print("Chain after: "+self.chain+"\n",file=sys.stderr)
                break
                             
            else:
                self.chain = self.chain+' '+' '.join(self.string.split(" ")[len(hook.split(' ')):])
                print("Chain after: "+self.chain+"\n",file=sys.stderr)
                
                hook = ' '.join(self.string.split(' ')[-2:])
                prev_chain = self.chain
                continue
            self.fetchDB(delete = True)    
        
        return self.chain

