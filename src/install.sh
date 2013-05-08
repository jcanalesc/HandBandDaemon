#!/bin/sh

echo "Instalando Python y dependencias"
apt-get -y install python2.7-dev python-pip python-mysqldb > /dev/null
echo "Instalando modulos de Python"
pip install python-daemon lockfile pycups PIL > /dev/null
echo "Creando estructura de directorios"
mkdir -p /usr/share/handbandd/tmp/
cp -v {handbandd.py,Code128b.py,configuracion.ini,BebasNeue.otf,logo.jpg} /usr/share/handbandd/
mkdir -p /var/{run,log}/handbandd/
touch /var/log/handbandd/handbandd.log
cp handbandd /etc/init.d/
chmod +x /etc/init.d/handbandd

echo -n "MySQL database user:"
read $user
echo -n "MySQL database password for user $user:"
read -s $pass
echo "Creando base de datos"
mysql -u $user --password=$pass < bdd.sql
echo "Instalando servicio"
update-rc.d handbandd enable
service handbandd start


