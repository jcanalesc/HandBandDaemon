import string
import MySQLdb
import ConfigParser
from datetime import datetime, timedelta
from utilidades import *


def getFromSerial(cx):
	message = "";
	while True:
		msg = cx.read(1)
		message += msg
		if msg == "\r":
			ans = ''.join(s for s in message if s in string.printable)
			log_this("respuesta: " + ans)
			return ans
		

def getParts(s):
	d = {}
	d['dir_torniquete'] = s[0:2]
	d['solicitud'] = s[2:3]
	resto = s[3:].split(".")
	d['codigo'] = resto[0]
	d['ingresos'] = int(resto[1][1:])
	d['salidas'] = int(resto[2][1:])
	d['no_pasos'] = int(resto[3][1:-2])
	return d

def reject(conn, comm_dict):
	sent_str = comm_dict['dir_torniquete'] + "N" + "\r"
	conn.write(sent_str)
	res = getFromSerial(conn)

	if res == sent_str:
		log_this("Comando aceptado: negar acceso a " + comm_dict['codigo'])
		return True
	else:
		return False

def accept(conn, comm_dict):
	sent_str = comm_dict['dir_torniquete'] + "A" + "\r"
	conn.write(sent_str)
	res = getFromSerial(conn)
	if res == sent_str:
		log_this("Comando aceptado: dar acceso a " + comm_dict['codigo'])
		# esperar la solicitud de paso:
		res = getParts(getFromSerial(conn))
		if res['solicitud'] == "S":
			#chequear si paso o no paso
			if res['ingresos'] > comm_dict['ingresos']:
				return True
			else:
				return False
		else:
			return False
	else:
		return False


def log_this(text):
	print "LOG: " + text
