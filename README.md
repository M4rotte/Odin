# Odin

Odin reads and writes shit.

## positional arguments

    DBNAME                Name of database (default : "Odin")

## optional arguments

    -h, --help            show this help message and exit
    -f FILE [FILE ...], --file FILE [FILE ...]
                        File(s) to read. Use '-' to read standard input.
    -s STRING [STRING ...], --string STRING [STRING ...]
                        String(s) to read. Use multiple arguments with caution
                        as it implies to load the whole DB for each one.
                        Consider concatenation.
    -n STRING, --next STRING
                        Get one string.
    -a STRING, --auto-next STRING
                        Get all strings from argument.
    -c STRING, --chain STRING
                        Get a chain of strings from argument.
    -N [INT], --fetch-by [INT]
                        How many records to work with before fetching the next
                        ones. Default is 8. Bigger means it will try more
                        times to get desired string before fetching next
                        results. Apply to -n, -a and -c options.
    -R, --random          Load database randomly, default is by most common
                        strings first. Apply to -n, -a and -c options.
    -M [INT], --max-results [INT]
                        Limit the number of records gathered on a complet
                        load. Default is 4096. This is useful on a big
                        database. Apply to -n, -a and -c options.
    -C STRING, --context STRING
                        Context to search with. It will be used in a WHERE
                        clause when loading strings from the database.
                        Searching for strings with any of the words provided
                        with this argument. You may not use regular
                        expressions there. Apply to -n, -a and -c options.
    -S [INT], --chain-size [INT]
                        Minimal number of words for a chain. Apply to -c
                        option only.
    -E [REGEXP], --chain-end [REGEXP]
                        Regexp to end a chain. Apply to -c option only.
                        
