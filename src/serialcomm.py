import serial
import select
import string
import MySQLdb
import ConfigParser
from datetime import datetime, timedelta

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

"""
while True:
	m = getParts(getFromSerial(conn))
	sent_str = ""
	while sent_str == "":
		ans = raw_input("El usuario %s quiere pasar. Aceptar? (s/n):" % m['codigo'])
		if ans == "s":
			sent_str = m['dir_torniquete'] + "S" + "\r"
		elif ans == "n":
			sent_str = m['dir_torniquete'] + "N" + "\r"
		else:
			print "Ingrese una respuesta valida."
	conn.write(sent_str)
	res = getFromSerial(conn)
	
	if res == sent_str:
		print "Comando aceptado."
	else:
		print "Tiempo de respuesta excedido."
"""

def reject(comm_dict):
	sent_str = comm_dict['dir_torniquete'] + "N" + "\r"
	conn.write(sent_str)
	res = getFromSerial(conn)

	if res == sent_str:
		log_this("Comando aceptado: negar acceso a " + comm_dict['codigo'])
		return True
	else:
		return False
def accept(comm_dict):
	sent_str = comm_dict['dir_torniquete'] + "A" + "\r"
	conn.write(sent_str)
	res = getFromSerial(conn)

	if res == sent_str:
		log_this("Comando aceptado: dar acceso a " + comm_dict['codigo'])
		# esperar la solicitud de paso:
		res = getParts(getFromSerial(conn))
		if res['solicitud'] == "S":
			return True
		else:
			return False
	else:
		return False

def log_this(text):
	print "LOG: " + text



if __name__ == "__main__":
	try:
		log_this("Inciando control de acceso")
		conn = serial.Serial()

		conn.baudrate = 38400
		conn.port = "/dev/ttyUSB0"
		#conn.nonblocking()

		conn.open()

		cp = ConfigParser.ConfigParser()
		cp.read("configuracion.ini")
		db =  MySQLdb.connect(host=cp.get("Database", "Host"),
							  user=cp.get("Database", "Username"),
							  passwd=cp.get("Database", "Password"),
							  db=cp.get("Database", "Dbname"))

		table = cp.get("Database", "Tablename")
		while True:
			m = getParts(getFromSerial(conn))
			if m['solicitud'] == "0": # entrada
				codigo_obtenido = m['codigo']
				dbh = db.cursor()
				count = dbh.execute("select estado, fecha_venta from %s where codigo = '%s'" % (table, codigo_obtenido))
				if count == 0:
					print "Codigo no valido"
					reject(m) or log_this("Error de comunicacion")
				else:
					linea = dbh.fetchone()
					if linea[0] == "0": # codigo no vendido aun
						print "Codigo no vendido"
						reject(m) or log_this("Error de comunicacion")
					elif linea[1] + timedelta(hours=12) < datetime.today(): # codigo vencido
						print "Codigo vencido"
						reject(m) or log_this("Error de comunicacion")
					else:
						print "Codigo valido"
						accept(m) or log_this("Error de comunicacion")
				db.commit()
				dbh.close()
			else:
				reject(m) or log_this("Error de comunicacion")
		db.close()
	except serial.SerialException as se:
		log_this("Problemas al intentar conectarse con la interfaz serial. (%s)" % str(se))
	except Exception as e:
		log_this(("Problema: (%s) " % (e.__class__.__name__)) + str(e))




