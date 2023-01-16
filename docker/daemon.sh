#!/bin/bash

signal-cli -u $1 daemon --dbus > /dev/null &
sleep 5
exec "${@:2}"
