#!/usr/bin/env bash
# Get all strings, count frequencies of apparition.
./odin -a "$1"  |sort |uniq -c |sort -nr
