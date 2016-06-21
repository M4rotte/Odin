#!/usr/bin/python3
# -*- coding: utf-8 -*-

import Odin
import argparse

argparser = argparse.ArgumentParser(description="Read and writes shit.")
argparser.add_argument("dbname", metavar='DBNAME', nargs="?", default="Odin", help="Name of database (default : \"Odin\")")
argparser.add_argument("-f", "--file", metavar="FILE", nargs="+", help="File(s) to read. Use '-' to read standard input.")
argparser.add_argument("-s", "--string", metavar="STRING", default="", nargs="+", help="String(s) to read. \
                                                                                        Use multiple arguments with caution as it implies to load the whole DB \
                                                                                        for each one. Consider concatenation.")
argparser.add_argument("-n", "--next", metavar="STRING", default="", nargs=1, help="Get one string.")
argparser.add_argument("-a", "--auto-next", metavar="STRING", default="", nargs=1, help="Get all strings from argument.")
argparser.add_argument("-c", "--chain", metavar="STRING", nargs=1, help="Get a chain of strings from argument.")


argparser.add_argument("-N", "--fetch-by", metavar="INT", type=int, default=8, nargs="?", help="How many records to work with before fetching the next ones. \
                                                                                                   Default is 8. \
                                                                                                   Bigger means it will try more times to get desired string \
                                                                                                   before fetching next results. \
                                                                                                   Apply to -n, -a and -c options.")
argparser.add_argument("-R", "--random", action="store_true", default=False , help="Load database randomly, default is by most common strings first. \
                                                                                      Apply to -n, -a and -c options.")
argparser.add_argument("-M", "--max-results", metavar="INT", type=int, default=4096, nargs="?", help="Limit the number of records gathered on a complet load. \
                                                                                                      Default is 4096. \
                                                                                                      This is useful on a big database. \
                                                                                                      Apply to -n, -a and -c options.")
argparser.add_argument("-C", "--context", metavar="STRING", default="", nargs=1,  help="Context to search with. It will be used in a WHERE clause \
                                                                                                    when loading strings from the database. Searching for strings \
                                                                                                    with any of the words provided with this argument. \
                                                                                                    Words are searched inside other words : 'foo bar' → '%foo%' OR '%bar%'. \
                                                                                                    You may not use regular expressions there. \
                                                                                                    Apply to -n, -a and -c options.")                                                                                                      
argparser.add_argument("-S", "--chain-size", metavar="INT", default=2, nargs="?",  help="Minimal number of words for a chain. \
                                                                                                    Apply to -c option only.")
                                                                                                    
argparser.add_argument("-E", "--chain-end", metavar="REGEXP", default="(.*)([A-Za-zéà ]+)(\.|\!|\?)$", nargs="?",\
                                                                                             help="Regexp to end a chain. \
                                                                                                   Default is '(.*)([A-Za-zéà ]+)(\.|\!|\?)( *)$' \
                                                                                                   Apply to -c option only.")

args = argparser.parse_args()

try:

    odin = Odin.Odin(args.dbname, STRING_MINWORDS = 2, STRING_MAXWORDS = 5)
    

    if (args.file):
        
        for f in args.file:
            odin.readFile(f)

    if (args.string):
        
        for s in args.string:
            odin.readString(s)

    if (args.random):
        odin.LOAD_ORDER = 'random'
        
    if (args.max_results):
        odin.MAX_RESULTS = args.max_results

    if (args.context):
        odin.CONTEXT = args.context[0]       
 
    if (args.chain_size):
        odin.CHAIN_MINWORDS = args.chain_size
        
    if (args.chain_end):
        odin.CHAIN_END = args.chain_end        
    
    if (args.fetch_by):
        odin.FETCH_BY = args.fetch_by
 
        
    if (args.next):

        odin.loadDB(odin.FETCH_BY,odin.LOAD_ORDER, odin.MAX_RESULTS, odin.CONTEXT)
        print(odin.getString(args.next[0]))

    if (args.auto_next):

        odin.loadDB(odin.FETCH_BY, odin.LOAD_ORDER, odin.MAX_RESULTS, odin.CONTEXT)
        ns = args.auto_next[0]
        while (ns != ''):
            ns = odin.getString(args.auto_next[0])
            if (ns):
                print(ns)
            if (len(odin.strings) < 3):
                odin.fetchDB()
                continue
    
    if (args.chain):
        odin.FETCH_BY = args.fetch_by
        print(odin.getChain(args.chain[0], minwords = odin.CHAIN_MINWORDS, end = odin.CHAIN_END))

except KeyboardInterrupt as e:
        odin.log("KeybaordInterrupt: "+odin.string+" "+str(len(odin.strings))+" "+str(odin.fetchcount))
        print("\nBye… ",e,file=sys.stderr)
        pass

exit(0)
