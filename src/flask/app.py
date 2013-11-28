# -*- coding: utf-8 -*-
import sys
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response, current_app
import bdd
import subprocess
import os
import random
import datetime
import locale
from functools import wraps, update_wrapper
from datetime import timedelta, datetime
import httplib2
import json

reload(sys)
sys.setdefaultencoding("utf-8")
locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
app = Flask(__name__)

CLAVE_ADMIN = "constitucion2013"

def crossdomain(origin=None, methods=None, headers=None,
	max_age=21600, attach_to_all=True,
	automatic_options=True):
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	if headers is not None and not isinstance(headers, basestring):
		headers = ', '.join(x.upper() for x in headers)
	if not isinstance(origin, basestring):
		origin = ', '.join(origin)
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()
	def get_methods():
		if methods is not None:
			return methods
		options_resp = current_app.make_default_options_response()
		return options_resp.headers['allow']
	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = current_app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
			if not attach_to_all and request.method != 'OPTIONS':
				return resp
			h = resp.headers
			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			return resp
		f.provide_automatic_options = False
		return update_wrapper(wrapped_function, f)
	return decorator


def nombremes(value):
	return ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][value-1]

app.jinja_env.filters["nombremes"] = nombremes

@app.route("/")
def main():
	if "logged_in" in session:
		session.pop("logged_in", None)
	e1, e2, e3, c1, c2, c3 = bdd.obtenerCantidades()
	cnt = (e1, e2, e3, c1, c2, c3)
	tot = (e1+c1, e2+c2, e3+c3)
	return render_template("main.html", cantidades=cnt, totales=tot)

@app.route("/genteActual")
@crossdomain(origin='*')
def get_gente_actual():
	ga = bdd.obtGenteActual()
	return jsonify({"res":ga})



@app.route("/emulaSalida")
def emula_salida():
	try:
		bdd.emula_salida()
		return jsonify({"res": True})
	except Exception as e:
		return jsonify({"res": False, "error": str(e)})

@app.route("/vaciar")
def vaciareg():
	try:
		bdd.vaciar()
		return jsonify({"res": True})
	except Exception as e:
		return jsonify({"res": False, "error": str(e)})		

@app.route("/agrega")
def agregaPersona():
	try:
		if request.args.get("cortesia", "") == "true":
			bdd.agregar(True)
		else:
			bdd.agregar(False)
		e1, e2, e3, c1, c2, c3 = bdd.obtenerCantidades()
		return jsonify({"res": True, "entradas_hoy": (e1,c1), "entradas_mes": (e2,c2), "entradas_total": (e3,c3)})
	except Exception as e:
		return jsonify({"res": False, "error": str(e)})

@app.route("/reportes")
def reportes():
	if "logged_in" in session:
		r_dia = bdd.get_reportes_dia()
		r_mes = bdd.get_reportes_mes()
		r_ano = bdd.get_reportes_ano()
		return render_template("reportes.html",rdia=r_dia, rmes=r_mes, rano=r_ano, now=datetime.now().strftime("%Y-%m-%d"))
	else:
		return render_template("login.html")

@app.route("/reporte/<int:ano>/<int:mes>/<int:dia>")
def reporte_diario(ano,mes,dia):
	datos = bdd.reportes_dia(ano, mes, dia)
	to = datetime.datetime(ano, mes, dia)
	pr = to.strftime("%A, %d de %B de %Y").decode("utf-8").capitalize()
	return render_template("reporte_dia.html", datos=datos, unidad_tiempo=u"día", periodo=pr)

@app.route("/reporte/<int:ano>/<int:mes>")
def reporte_mensual(ano,mes):
	datos = bdd.reportes_mes(ano, mes)
	to = datetime.datetime(ano, mes, 1)
	pr = to.strftime("%B de %Y").decode("utf-8").capitalize()
	return render_template("reporte_mes.html", datos=datos, unidad_tiempo=u"mes", periodo=pr)

@app.route("/reporte/<int:ano>")
def reporte_anual(ano):
	datos = bdd.reportes_ano(ano)
	to = datetime.datetime(ano, 1, 1)
	pr = to.strftime("%Y").decode("utf-8").capitalize()
	return render_template("reporte_ano.html", datos=datos, unidad_tiempo=u"año", periodo=pr)

app.secret_key = 'IMSNNNDksmdlkd[]][]/2nbbc7slla20cfmci883'

@app.route("/login", methods=['POST'])
def logear():
	passwd = request.form['passwd']
	if passwd == CLAVE_ADMIN:
		session["logged_in"] = True
		return redirect(url_for("reportes"))
	else:
		return render_template("login.html", msg="Clave incorrecta.")

@app.route("/applogin")
@crossdomain(origin='*')
def logea_movil():
	user = request.args.get("user", None)
	pswd = request.args.get("pass", None)

	obj = {
		"success": True
	}

	return jsonify(obj)


@app.route("/appdata")
@crossdomain(origin='*')
def obt_datos_app():
	objeto = {}
	tiporeporte = request.args.get("tiporeporte", None)
	fechareporte = [int(x) for x in request.args.get("reporte", None).split("/")] if request.args.get("reporte", None).find("/") != -1 else request.args.get("reporte", None)
	objeto["reportes"] = {}
	objeto["reportes"]["dia"] = []
	objeto["reportes"]["mes"] = []
	objeto["reportes"]["ano"] = []
	r_dia = bdd.get_reportes_dia()
	r_mes = bdd.get_reportes_mes()
	r_ano = bdd.get_reportes_ano()
	for elem in r_dia:
		objeto["reportes"]["dia"].append([elem.day, elem.month, elem.year])
	for elem in r_mes:
		objeto["reportes"]["mes"].append([elem.month, elem.year])
	for elem in r_ano:
		objeto["reportes"]["ano"].append(elem.year)
	objeto["reporte"] = {
		"datos_grafico": [],
		"stats": []
	}
	report_data = None
	if tiporeporte == "dia":
		report_data = bdd.reportes_dia(fechareporte[2], fechareporte[1], fechareporte[0])
		objeto["reporte"]["datos_grafico"] = report_data["flujos"]
		objeto["reporte"]["stats"] = [
		{"label": "Total", "value" : str(sum(report_data["entradas_vendidas"]))},
		{"label": "Peak" , "value" : str(report_data["peak"][0])},
		{"label": "Tiempo pr.", "value": "{0:.1f}".format(report_data["tiempo_promedio"])+"min"}
		]
	elif tiporeporte == "mes":
		report_data = bdd.reportes_mes(fechareporte[1], fechareporte[0])
		objeto["reporte"] = {
			"datos_grafico" : report_data["flujos"],
			"stats": [
				{"label": "Total", "value": sum(report_data["entradas_vendidas"])},
				{"label": u"Mejor día", "value": report_data["mejordia"]["dia"]},
				{"label": u"Cant. mejor día", "value": report_data["mejordia"]["entradas"]}
			]
		}
	elif tiporeporte == "ano":
		report_data = bdd.reportes_ano(fechareporte)
		objeto["reporte"] = {
			"datos_grafico": report_data["flujos"],
			"stats": [
				{"label": "Total", "value": sum(report_data["entradas_vendidas"])},
				{"label": "Mejor mes", "value": report_data["mejormes"]["mes"]},
				{"label": "Cant. mejor mes", "value": report_data["mejormes"]["entradas"]}
			]
		}
	return jsonify(objeto)

@app.route("/mkevento", methods=["POST"])
def genera_evento():
	fecha = request.form["fecha"]
	nombre = request.form["nombre"]
	nentradas = request.form["nentradas"]
	res = bdd.genera_evento(fecha=fecha, nombre=nombre, nentradas=nentradas)
	return jsonify(res)

@app.route("/ingresarSocio/")
def ingresasocio():
	rutsocio = request.args.get("rut", None)
	res = { 'success': True }
	try:
		bdd.imprimeSocio(rutsocio)
	except:
		res["success"] = False
	return jsonify(res)

@app.route("/syncUserDB")
def sincroniza():
	res = {'success': True}
	try:
		ho = httplib2.Http(".cache")
		resp, content = ho.request("http://186.64.120.145:5000/userdb/download/")
		obj = json.loads(content)
		bdd.insertaUsuarios(obj)
	except:
		res["success"] = False
	return jsonify(res)

if __name__ == "__main__":
	app.run("0.0.0.0",debug=True)