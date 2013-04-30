import serial
import select
import string

conn = serial.Serial()

conn.baudrate = 38400
conn.port = "/dev/ttyUSB0"
#conn.nonblocking()

conn.open()

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
	d['lrc'] = resto[3][-2:]

	return d

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



