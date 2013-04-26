#!/bin/sh

apt-get -y install python2.7-dev python-pip python-mysqldb
pip install python-daemon lockfile pycups PIL

mkdir -p /usr/share/handbandd
cp handbandd.py /usr/share/handbandd/
cp Code128b.py /usr/share/handbandd/
