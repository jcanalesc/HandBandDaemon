# -*- coding: utf-8 -*-
import serial
import select
import string
import MySQLdb
import os
import ConfigParser
from datetime import datetime, timedelta
from utilidades import *

WDIR="/usr/share/handbandd/"

if __name__ == "__main__":
	os.chdir(WDIR)
	try:
		log_this("Iniciando control de acceso")
		cx = serial.Serial()

		cx.baudrate = 38400
		cx.port = "/dev/ttyUSB0"
		#conn.nonblocking()

		cx.open()

		cp = ConfigParser.ConfigParser()
		cp.read("configuracion.ini")
		

		table = cp.get("Database", "Tablename")
		while True:
			db =  MySQLdb.connect(host=cp.get("Database", "Host"),
							  user=cp.get("Database", "Username"),
							  passwd=cp.get("Database", "Password"),
							  db=cp.get("Database", "Dbname"))
			m = getParts(getFromSerial(cx))
			if m['solicitud'] == "0": # entrada
				codigo_obtenido = m['codigo']
				if len(codigo_obtenido) < 4:
					log_this("Codigo leido incorrectamente")
					reject(cx, m)
				elif codigo_maestro(codigo_obtenido):
					log_this("Codigo maestro ingresado")
					accept(cx, m)
				else:
					dbh = db.cursor()
					count = dbh.execute("select estado, fecha_venta from %s where codigo = '%s'" % (table, codigo_obtenido))
					if count == 0:
						print "Codigo no valido"
						reject(cx, m) or log_this("Error de comunicacion")
					else:
						linea = dbh.fetchone()
						if linea[0] == "0": # codigo no vendido aun
							print "Codigo no vendido"
							reject(cx, m) 
						elif linea[1] + timedelta(hours=12) < datetime.today(): # codigo vencido
							print "Codigo vencido"
							reject(cx, m)
						elif linea[1] > datetime.today():
							print "Codigo no corresponde a la fecha actual"
							reject(cx, m)
						else:
							# obtengo el último movimiento del codigo en cuestion
							l = dbh.execute("select tipo, codigo, fecha from historial where codigo = '%s' order by fecha desc limit 1" % codigo_obtenido)
							rowb = dbh.fetchone()
							if l == 0 or rowb[0] == "Salida":
								print "Codigo valido"
								if accept(cx, m):
									dbh2 = db.cursor()
									dbh2.execute("insert into historial (codigo) values ('%s')" % m['codigo'])
								else:
									log_this("El codigo '%s' no ingresó" % m['codigo'])
							else:
								reject(cx, m)
								print "El codigo '%s' ya entró y no ha salido" % codigo_obtenido
				db.commit()
				dbh.close()
			else:
				reject(cx, m) or log_this("Error de comunicacion")
			db.close()
	except serial.SerialException as se:
		log_this("Problemas al intentar conectarse con la interfaz serial. (%s)" % str(se))
	except Exception as ex:
		log_this(str(ex))
		exit(0)



