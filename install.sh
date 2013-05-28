#!/bin/sh

echo "Instalando Python y dependencias" &&
apt-get -y install python2.7-dev python-pip python-mysqldb apache2 libapache2-mod-wsgi &&
echo "Instalando modulos de Python" &&
pip install python-daemon lockfile pycups PIL Flask &&
echo "Creando estructura de directorios" &&
mkdir -p /usr/share/handbandd/tmp/ &&
cp -R src/* /usr/share/handbandd/ &&
mkdir -p /var/{run,log}/handbandd/ &&
touch /var/log/handbandd/handbandd.log &&


echo -n "MySQL database user:" &&
read user &&
echo -n "MySQL database password for user $user:" &&
read pass &&
echo "Creando base de datos" &&
mysql -u $user --password=$pass < src/bdd.sql &&

echo "Instalando frontend" &&
a2enmod wsgi &&
cp src/monitoreo /etc/apache2/sites-available/ &&
a2ensite monitoreo &&
service apache2 reload &&

echo "Instalando servicio" &&
cp handbandd.conf /etc/init/ &&
service handbandd start


