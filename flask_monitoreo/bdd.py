import MySQLdb

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