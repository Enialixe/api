#!/bin/sh

if [ "$1" = "stop" ]; then
    echo "stop"
    sudo service redis stop
else
    echo "start"
    sudo service redis start
fi
