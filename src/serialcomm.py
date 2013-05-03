import serial
import select
import string
import MySQLdb
import ConfigParser

def getFromSerial(cx):
	message = "";
	while True:
		[x,y,z] = select.select([conn], [], [])
		buff = x[0]
		msg = buff.read(buff.inWaiting())
		message += msg
		if msg[-1] == "\r":
			return ''.join(s for s in message if s in string.printable)
		

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
		return True
	else:
		return False
def accept(comm_dict):
	sent_str = comm_dict['dir_torniquete'] + "A" + "\r"
	conn.write(sent_str)
	res = getFromSerial(conn)

	if res == sent_str:
		return True
	else:
		return False

def log_this(text):
	print "LOG: " + text

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
	dbh = db.cursor()

	table = cp.get("Database", "Tablename")
	while True:
		m = getParts(getFromSerial(conn))
		codigo_obtenido = m['codigo']
		count = dbh.execute("select estado, fecha_venta from %s where codigo = '%s'" % (table, codigo_obtenido))
		if count == 0:
			reject(m) or log_this("Error de comunicacion")
		else:
			linea = dbh.fetch_row()
			if linea[0] != "0": # codigo no vendido aun
				reject(m) or log_this("Error de comunicacion")
			else:
				accept(m) or log_this("Error de comunicacion")

	dbh.close()
	db.close()
except serial.SerialException as se:
	log_this("Problemas al intentar conectarse con la interfaz serial. (%s)" % str(se))
except Exception as e:
	log_this(("Problema: (%s) " % (e.__class__.__name__)) + str(e))




