#!/bin/sh

until python /usr/share/handbandd/serialcomm.py >> /var/log/handbandd/entrada.log 2>&1; do
	echo "restarting" >&2
	sleep 1
done