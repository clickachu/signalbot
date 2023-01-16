#!/bin/bash

signal-cli -u $1 daemon --no-receive-stdout --dbus &
sleep 5
exec "${@:2}"
