#!/bin/sh
until python /usr/share/handbandd/controlsalida.py; do
	echo "restarting" >&2
	sleep 1
done
