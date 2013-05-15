import serial
from utilidades import *

if __name__ == "__main__":
	# torniquete de salida
	try:
		log_this("Inciando control de salida")
		cx = serial.Serial()

		cx.baudrate = 38400
		## ATENCION: asegurarse de que el torniquete de salida se conecte DESPUES para que le quede asignado el ttyUSB1 en vez del 0.
		cx.port = "/dev/ttyUSB0"
		#conn.nonblocking()

		cx.open()

		cp = ConfigParser.ConfigParser()
		cp.read("configuracion.ini")
		db =  MySQLdb.connect(host=cp.get("Database", "Host"),
							  user=cp.get("Database", "Username"),
							  passwd=cp.get("Database", "Password"),
							  db=cp.get("Database", "Dbname"))

		while True:
			m = getParts(getFromSerial(cx))
			codigo_obt = m['codigo']
			dbh = db.cursor()
			# criterio para la salida?
			# defecto: siempre aceptar
			if accept(cx, m):
				dbh.execute("insert into historial (tipo, codigo) values ('Salida', '%s')" % codigo_obt)
			db.commit()
			dbh.close()
	except serial.SerialException as se:
		log_this("Problemas al intentar conectarse con la interfaz serial. (%s)" % str(se))
	except Exception as e:
		log_this(("Problema: (%s) " % (e.__class__.__name__)) + str(e))
	exit(1)
