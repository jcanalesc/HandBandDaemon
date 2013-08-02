import MySQLdb
import random
import datetime
import time
import ConfigParser

cp = ConfigParser.ConfigParser()
cp.read("../configuracion.ini")
connect_dict = {
	"host": cp.get("Database", "Host"),
	"user": cp.get("Database", "Username"),
	"passwd": cp.get("Database", "Password"),
	"db": cp.get("Database","Dbname")
}



def obtGenteActual():
	connection = MySQLdb.connect(**connect_dict)
	cur = connection.cursor()
	resc = 0
	resg = 0
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
	return (resc+resg,resc, resg)

def emula_salida():
	connection = MySQLdb.connect(**connect_dict)
	cur = connection.cursor()
	cur.execute("insert into historial (codigo, tipo) values ('x', 'Salida')")
	connection.commit()
	cur.close()
	connection.close()
	return True

def vaciar():
	connection = MySQLdb.connect(**connect_dict)
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
	connection = MySQLdb.connect(**connect_dict)
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
	connection = MySQLdb.connect(**connect_dict)
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
	connection = MySQLdb.connect(**connect_dict)
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
	connection = MySQLdb.connect(**connect_dict)
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
	connection = MySQLdb.connect(**connect_dict)
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
	x = 0
	y = 0
	fecha_reporte = "%s-%02d-%02d" % (ano, mes, dia)
	connection = MySQLdb.connect(**connect_dict)
	cur = connection.cursor()
	lines = cur.execute("select count(*), segmento from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) = '%s' and segmento = 0" % fecha_reporte)
	if lines > 0:
		x = cur.fetchone()
		entradas_vendidas = int(x[0])
	lines2 = cur.execute("select count(*), segmento from codigos where DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) = '%s' and segmento = 1" % fecha_reporte)
	if lines2 > 0:
		y = cur.fetchone()
		evc = int(y[0])
	cur.execute("select tipo, fecha, UNIX_TIMESTAMP(TIMESTAMPADD(HOUR,-4,fecha)) as uts, codigo from historial where DATE(TIMESTAMPADD(HOUR,-6,fecha)) = '%s' order by fecha " % fecha_reporte)

	periodo = (60*20) # 20 minutos
	conteo = 0
	maximo = 0
	ini_max = datetime.date(1960,1,1)
	fin_max = datetime.date(1960,1,1)
	flujo = []
	# intervalos de 20 minutos
	entradas = [0 for i in range((24*3600) / periodo)]
	salidas = [0 for i in range((24*3600) / periodo)]

	diferencia = -1
	hora_inicio = 0

	historial = {}
	estancias = []

	for row in cur.fetchall():
		if row[3] not in historial:
			historial[row[3]] = []
		if diferencia == -1:
			diferencia = int(row[2])
			hora_inicio = row[2]
		if row[0] == "Entrada":
			conteo += 1
			historial[row[3]].append(row[2])
			entradas[(int(row[2]) - diferencia)/(periodo)] += 1
		else:
			conteo -= 1
			if len(historial[row[3]]) > 0:
				estancias.append(row[2] - historial[row[3]].pop())
			salidas[(int(row[2]) - diferencia)/(periodo)] += 1


		flujo.append([int(row[2])*1000,conteo])
		if conteo > maximo:
			maximo = conteo
			ini_max = fin_max = row[1]
		if conteo == maximo:
			fin_max = row[1]
	tiempo_promedio = 0.0
	if len(estancias) > 0:
		tiempo_promedio = (sum(estancias) / float(len(estancias))) / 60.0 # en minutos

	entradas2 = [[(int(hora_inicio) + (periodo) * i)*1000, entradas[i]] for i in range(len(entradas))]
	salidas2 = [[(int(hora_inicio) + (periodo) * i)*1000, salidas[i]] for i in range(len(salidas))]


	return {"entradas_vendidas": [entradas_vendidas,evc], "peak": [maximo, ini_max, fin_max], "flujos": flujo, "entradas" : entradas2, "salidas": salidas2, "tiempo_promedio" : tiempo_promedio}

def reportes_mes(ano, mes):
	fecha_reporte = "%s-%02d-01" % (ano, mes)
	connection = MySQLdb.connect(**connect_dict)
	cur = connection.cursor()

	vta_gral = []
	vta_cort = []
	vta_total = {}

	cur.execute("select COUNT(*) as c, DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) as df from codigos where MONTH(TIMESTAMPADD(HOUR,-6,fecha_venta)) = MONTH('%s') and YEAR(TIMESTAMPADD(HOUR,-6,fecha_venta)) = YEAR('%s') and segmento = 0 group by df" % (fecha_reporte, fecha_reporte))
	
	vta_gral = cur.fetchall()

	cur.execute("select COUNT(*) as c, DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) as df from codigos where MONTH(TIMESTAMPADD(HOUR,-6,fecha_venta)) = MONTH('%s') and YEAR(TIMESTAMPADD(HOUR,-6,fecha_venta)) = YEAR('%s') and segmento = 1 group by df" % (fecha_reporte, fecha_reporte))

	vta_cort = cur.fetchall()
	ev = 0
	evc = 0

	for xg in vta_gral:
		ev += xg[0]
		if xg[1] in vta_total:
			vta_total[xg[1]] += xg[0]
		else:
			vta_total[xg[1]] = xg[0]

	for xc in vta_cort:
		evc += xc[0]
		if xc[1] in vta_total:
			vta_total[xc[1]] += xc[0]
		else:
			vta_total[xc[1]] = xc[0]

	tdy = datetime.date(ano, mes, 1)
	target_month = tdy.month+1
	target_year = tdy.year
	if target_month > 12:
		target_month = 1
		target_year = target_year + 1
	target_date = datetime.date(target_year, target_month, 1)
	while tdy < target_date:
		if tdy not in vta_total:
			vta_total[tdy] = 0
		tdy = tdy + datetime.timedelta(days=1)
	mejor_dia = datetime.date(1960,1,1)
	mejor_venta = 0
	flujo = []

	for k, v in sorted(vta_total.iteritems()):
		flujo.append([int(time.mktime(k.timetuple()))*1000, int(v)])
		if v > mejor_venta:
			mejor_venta = v
			mejor_dia = k


	return {"entradas_vendidas": [int(ev), int(evc)], "mejordia": { "dia" : mejor_dia.strftime("%Y-%m-%d"), "entradas" : int(mejor_venta)}, "flujos" : flujo}

def reportes_ano(ano):
	fecha_reporte = "%d-01-01" % ano
	connection = MySQLdb.connect(**connect_dict)
	cur = connection.cursor()

	vta_gral = []
	vta_cort = []
	vta_total = {}

	cur.execute("select COUNT(*) as c, DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) as df, MONTH(TIMESTAMPADD(HOUR, -6, fecha_venta)) as mf from codigos where YEAR(TIMESTAMPADD(HOUR,-6,fecha_venta)) = YEAR('%s') and segmento = 0 group by mf" % (fecha_reporte))
	
	vta_gral = cur.fetchall()

	cur.execute("select COUNT(*) as c, DATE(TIMESTAMPADD(HOUR,-6,fecha_venta)) as df, MONTH(TIMESTAMPADD(HOUR, -6, fecha_venta)) as mf from codigos where YEAR(TIMESTAMPADD(HOUR,-6,fecha_venta)) = YEAR('%s') and segmento = 1 group by mf" % (fecha_reporte))

	vta_cort = cur.fetchall()

	ev = 0
	evc = 0

	for xg in vta_gral:
		ev += xg[0]
		if xg[2] in vta_total:
			vta_total[xg[2]] += xg[0]
		else:
			vta_total[xg[2]] = xg[0]

	for xc in vta_cort:
		evc += xc[0]
		if xc[2] in vta_total:
			vta_total[xc[2]] += xc[0]
		else:
			vta_total[xc[2]] = xc[0]

	mejor_mes = 1
	mejor_venta = 0
	flujo = []

	for i in range(1,13):
		if i not in vta_total:
			vta_total[i] = 0

	for k, v in sorted(vta_total.iteritems()):
		flujo.append([int(time.mktime(datetime.date(ano, k, 1).timetuple()))*1000, int(v)])
		if v > mejor_venta:
			mejor_venta = v
			mejor_mes = k


	return {"entradas_vendidas": [int(ev), int(evc)], "mejormes": {"mes" : datetime.date(ano, int(mejor_mes), 1).strftime("%B"), "entradas": mejor_venta}, "flujos": flujo}








