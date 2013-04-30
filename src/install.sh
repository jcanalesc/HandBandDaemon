#!/bin/sh

apt-get -y install python2.7-dev python-pip python-mysqldb
pip install python-daemon lockfile pycups PIL

mkdir -p /usr/share/handbandd/tmp
cp {handbandd.py,Code128b.py,configuracion.ini} /usr/share/handbandd/
mkdir -p /var/{run,log}/handbandd
touch /var/log/handbandd/handbandd.log

echo -n "MySQL database user:"
read $user
echo -n "MySQL database password for user $user:"
read -s $pass
mysql -u $user --password=$pass < bdd.sql

update-rc.d handbandd enable
service handbandd start

