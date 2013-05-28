import MySQLdb
import random

connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")

def obtGenteActual():
	cur = connection.cursor()
	cur.execute("select tipo, count(*) as conteo from historial group by tipo")

	res = 0


	for row in cur.fetchall():
		if row[0] == "Entrada":
			res += row[1]
		else:
			res -= row[1]
	connection.commit()
	cur.close()
	return res

def emula_salida():
	cur = connection.cursor()
	cur.execute("insert into historial (codigo, tipo) values ('x', 'Salida')")
	connection.commit()
	cur.close()
	return True

def vaciar():
	cur = connection.cursor()
	cur.execute("truncate historial")
	connection.commit()
	cur.close()
	return True

def agregar():
	cur = connection.cursor()
	cur.execute("select max(codigo) as mc from codigos where segmento = 0")
	linea = cur.fetchone()
	codigosgte = 0
	if linea[0] != None:
		codigosgte = int(linea[0]) + 1
	else:
		codigosgte = 1
	cur.execute("insert into codigos (codigo, estado, segmento) values ('%06d', 1, 0)" % codigosgte)
	connection.commit()
	cur.close()
	return True