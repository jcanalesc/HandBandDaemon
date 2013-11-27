#!/bin/sh
echo "Instalando Python y dependencias" &&
apt-get -y install python2.7-dev python-pip python-mysqldb apache2 libapache2-mod-wsgi python-serial cups &&
echo "Instalando modulos de Python" &&
pip install python-daemon lockfile pycups Pillow Flask &&
echo "Creando estructura de directorios" &&
mkdir -p /usr/share/handbandd/tmp/ &&
cp -R src/* /usr/share/handbandd/ &&
mkdir -p /var/run/handbandd/ &&
mkdir -p /var/log/handbandd/ &&
touch /var/log/handbandd/handbandd.log &&

echo -n "Supersuario MySQL:" &&
read user &&
echo -n "Contraseña para el usuario '$user'" &&
read pass &&
echo "Creando base de datos" &&
mysql -u $user --password=$pass < src/bdd.sql &&

echo "Instalando frontend" &&
a2enmod wsgi &&
cp src/monitoreo /etc/apache2/sites-available/ &&
a2ensite monitoreo &&
service apache2 reload &&

DEFAULT_PRINTER = $(lpstat -d | awk '{print $4}')
echo "Instalando $DEFAULT_PRINTER como impresora de pulseras"
echo "Default=$DEFAULT_PRINTER" >> src/configuracion.ini

echo "Instalando servicio" &&
cp handbandd.conf /etc/init/ &&
service handbandd start

echo "Instalando demonio para torniquete de entrada" &&
cp torniquete1.conf /etc/init/torniquete.conf
service torniquete start


