import MySQLdb
import random
import datetime


def obtGenteActual():
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	
	cur.execute("select tipo, count(*) as conteo from historial group by tipo")

	res = 0
	resc = 0
	resg = 0


	for row in cur.fetchall():
		if row[0] == "Entrada":
			res += row[1]
		else:
			res -= row[1]
	
	cur.execute("select tipo, count(*) as conteo from (select tipo from historial left join codigos on (historial.codigo = codigos.codigo) where codigos.segmento = 1) as f group by tipo")
	for row in cur.fetchall():
		if row[0] == "Entrada":
			resc += row[1]
		else:
			resc -= row[1]
	cur.execute("select tipo, count(*) as conteo from (select tipo from historial left join codigos on (historial.codigo = codigos.codigo) where codigos.segmento = 0) as f group by tipo")
	for row in cur.fetchall():
		if row[0] == "Entrada":
			resg += row[1]
		else:
			resg -= row[1]


	connection.commit()
	cur.close()
	connection.close()
	return (res,resc, resg)

def emula_salida():
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	cur.execute("insert into historial (codigo, tipo) values ('x', 'Salida')")
	connection.commit()
	cur.close()
	connection.close()
	return True

def vaciar():
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	cur.execute("select codigo, tipo from (select * from historial order by fecha desc) as f group by codigo")
	codigos = cur.fetchall()
	for row in codigos:
		if row[1] == "Entrada":
			cur.execute("insert into historial (tipo, codigo) values ('Salida', '%s')" % row[0])
	connection.commit()
	cur.close()
	connection.close()
	return True

def agregar(cortesia):
	seg = 0
	if cortesia:
		seg = 1
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	cur.execute("select max(codigo) as mc from codigos")
	linea = cur.fetchone()
	codigosgte = 0
	if linea[0] != None:
		codigosgte = int(linea[0]) + 1
	else:
		codigosgte = 1
	cur.execute("insert into codigos (codigo, estado, segmento) values ('%06d', 1, %d)" % (codigosgte, seg))
	if cortesia:
		cur.execute("insert into historial (codigo) values ('%06d')" % codigosgte)
	connection.commit()
	cur.close()
	connection.close()
	return True

def obtenerCantidades():
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	cur.execute("select count(*), segmento from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) = DATE(TIMESTAMPADD(HOUR,-6,NOW())) and segmento = 0")
	e_hoy = cur.fetchone()[0]
	cur.execute("select count(*), segmento from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) = DATE(TIMESTAMPADD(HOUR,-6,NOW())) and segmento = 1")
	e_hoy_c = cur.fetchone()[0]
	cur.execute("select count(*), segmento from codigos where MONTH(TIMESTAMPADD(HOUR,-6,fecha_venta)) = MONTH(TIMESTAMPADD(HOUR,-6,NOW())) and YEAR(TIMESTAMPADD(HOUR,-6,fecha_venta)) = YEAR(TIMESTAMPADD(HOUR,-6,NOW())) and segmento = 0")
	e_mes = cur.fetchone()[0]
	cur.execute("select count(*), segmento from codigos where MONTH(TIMESTAMPADD(HOUR,-6,fecha_venta)) = MONTH(TIMESTAMPADD(HOUR,-6,NOW())) and YEAR(TIMESTAMPADD(HOUR,-6,fecha_venta)) = YEAR(TIMESTAMPADD(HOUR,-6,NOW())) and segmento = 1")
	e_mes_c = cur.fetchone()[0]
	cur.execute("select count(*), segmento from codigos where segmento = 0")
	e_total = cur.fetchone()[0]
	cur.execute("select count(*), segmento from codigos where segmento = 1")
	e_total_c = cur.fetchone()[0]
	connection.commit()
	cur.close()
	connection.close()
	return (e_hoy, e_mes, e_total, e_hoy_c, e_mes_c, e_total_c)

"""
	FUNCIONES DE REPORTES
"""
def get_reportes_dia():
	#ultimos 10 dias
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	start_date = datetime.datetime.today() - datetime.timedelta(days=10)
	start_date_string = start_date.strftime("%Y-%m-%d %H:%M:%S")
	cur.execute("select DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) as df from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) >= DATE(TIMESTAMPADD(HOUR,-6, '%s')) group by df order by df desc limit 10" % start_date_string)
	res = []
	for row in cur.fetchall():
		res.append(row[0])
	cur.close()
	connection.close()
	return res

def get_reportes_mes():
	#ultimos 10 meses
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	tdy = datetime.datetime.today()
	target_month = tdy.month - 10
	target_year = tdy.year
	if target_month <= 0:
		target_month = 12 + target_month
		target_year = target_year - 1
	start_date = datetime.datetime(target_year,target_month, 1)
	start_date_string = start_date.strftime("%Y-%m-%d %H:%M:%S")
	cur.execute("select DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) as df, CONCAT(YEAR(DATE(TIMESTAMPADD(HOUR,-6,fecha_venta))),'-',MONTH(DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)))) as my from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) >= '%s' group by my order by my desc limit 10" % start_date_string)
	res = []
	for row in cur.fetchall():
		res.append(row[0])
	return res

def get_reportes_ano():
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	tdy = datetime.datetime.today()
	start_date = datetime.datetime(tdy.year-1,1, 1)
	start_date_string = start_date.strftime("%Y-%m-%d %H:%M:%S")
	cur.execute("select DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) as df, YEAR(DATE(TIMESTAMPADD(HOUR,-6,fecha_venta))) as ye from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) >= '%s' group by ye order by ye desc limit 10" % start_date_string)
	res = []
	for row in cur.fetchall():
		res.append(row[0])
	return res

def reportes_dia(ano, mes, dia):
	# entradas vendidas total
	fecha_reporte = "%s-%02d-%02d" % (ano, mes, dia)
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	cur.execute("select count(*), segmento from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) = '%s' and segmento = 0" % fecha_reporte)
	x = cur.fetchone()
	entradas_vendidas = int(x[0])
	cur.execute("select count(*), segmento from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) = '%s' and segmento = 1" % fecha_reporte)
	y = cur.fetchone()
	evc = int(y[0])
	print fecha_reporte
	cur.execute("select tipo, fecha, UNIX_TIMESTAMP(TIMESTAMPADD(HOUR,-4,fecha)) as uts from historial where DATE(TIMESTAMPADD(HOUR,-6,fecha)) = '%s' order by fecha " % fecha_reporte)

	conteo = 0
	maximo = 0
	ini_max = ""
	fin_max = ""
	flujo = []

	for row in cur.fetchall():
		print row
		if row[0] == "Entrada":
			conteo += 1
		else:
			conteo -= 1
		flujo.append([int(row[2])*1000,conteo])
		if conteo > maximo:
			maximo = conteo
			ini_max = fin_max = row[1]
		if conteo == maximo:
			fin_max = row[1]
	return {"entradas_vendidas": [entradas_vendidas,evc], "peak": [maximo, ini_max, fin_max], "flujos": flujo}

def reportes_mes(ano, mes):
	fecha_reporte = "%s-%02d-01" % (ano, mes)
	connection = MySQLdb.connect(host="localhost", user="testuser", passwd="handband", db="constitucion")
	cur = connection.cursor()
	cur.execute("select count(*), segmento from codigos where MONTH(TIMESTAMPADD(HOUR,-6,fecha_venta)) = MONTH('%s') and YEAR(TIMESTAMPADD(HOUR,-6,fecha_venta)) = YEAR('%s') and segmento = 0" % (fecha_reporte, fecha_reporte))
	e_mes = cur.fetchone()[0]
	cur.execute("select count(*), segmento from codigos where MONTH(TIMESTAMPADD(HOUR,-6,fecha_venta)) = MONTH('%s') and YEAR(TIMESTAMPADD(HOUR,-6,fecha_venta)) = YEAR('%s') and segmento = 1" % (fecha_reporte, fecha_reporte))
	e_mes_c = cur.fetchone()[0]

	return {"entradas_vendidas": [ev, evc], "mejordia": { "dia" : md, "entradas" : mde}, "flujos" : flujo}
