import serial
from utilidades import *
import os


WDIR = "/usr/share/handbandd/"
if __name__ == "__main__":
	# torniquete de salida
	try:
		os.chdir(WDIR)
		log_this("Iniciando control de salida")
		cx = serial.Serial()

		cx.baudrate = 38400
		## ATENCION: asegurarse de que el torniquete de salida se conecte DESPUES para que le quede asignado el ttyUSB1 en vez del 0.
		cx.port = "/dev/ttyUSB0"
		#conn.nonblocking()

		cx.open()

		cp = ConfigParser.ConfigParser()
		cp.read("configuracion.ini")
		

		while True:
			
			m = getParts(getFromSerial(cx))
			codigo_obt = m['codigo']
			# criterio para la salida?
			# defecto: siempre aceptar
			if len(m['codigo']) < 4:
				log_this("Codigo leido incorrectamente")
				reject(cx, m)
			elif accept(cx, m):
				if not codigo_maestro(codigo_obt):
					db = MySQLdb.connect(host=cp.get("Database", "Host"),user=cp.get("Database", "Username"),passwd=cp.get("Database", "Password"),db=cp.get("Database", "Dbname"))
					dbh = db.cursor()
					lines = dbh.execute("select tipo from historial where codigo = '%s' order by fecha desc limit 1" % codigo_obt)
					if lines > 0 and dbh.fetchone()[0] == "Entrada":
						dbh.execute("insert into historial (tipo, codigo) values ('Salida', '%s')" % codigo_obt)
					db.commit()
					dbh.close()
					db.close()
				else:
					log_this("Codigo maestro ingresado")
	except serial.SerialException as se:
		log_this("Problemas al intentar conectarse con la interfaz serial. (%s)" % str(se))
	except Exception as e:
		log_this(("Problema: (%s) " % (e.__class__.__name__)) + str(e))
	exit(1)
