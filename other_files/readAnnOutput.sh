#!/bin/bash

counter=0

# Read from YARP and process each line
yarp read ... /annabell/output | while read l; do 
    ((counter++))
    # monitoring
    echo "Line $counter - Read from YARP: $l"
    # to the output file
    echo "$l" > /home/asad/annabell/annadoc/annabell.txt
done

