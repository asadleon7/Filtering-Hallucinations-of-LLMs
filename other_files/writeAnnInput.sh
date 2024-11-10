#!/bin/bash

FILENAME="/home/asad/annabell/annadoc/toAnnabell.txt"

# Printing a message 
echo "Starting inotifywait to monitor $FILENAME"

# Use of inotifywait to monitor the file continuously
while true; do
    inotifywait -e modify "$FILENAME"
    echo "Change detected in $FILENAME"
    yarp write ... /annabell/input < "$FILENAME"
done

