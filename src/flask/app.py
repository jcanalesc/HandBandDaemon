# -*- coding: utf-8 -*-
import sys
from flask import Flask, render_template, jsonify, request
import bdd
import subprocess
import os
import random
import datetime
import locale
locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
app = Flask(__name__)

@app.route("/")
def main():
    e1, e2, e3, c1, c2, c3 = bdd.obtenerCantidades()
    cnt = (e1, e2, e3, c1, c2, c3)
    tot = (e1+c1, e2+c2, e3+c3)
    return render_template("main.html", cantidades=cnt, totales=tot)

@app.route("/genteActual")
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
	r_dia = bdd.get_reportes_dia()
	r_mes = bdd.get_reportes_mes()
	r_ano = bdd.get_reportes_ano()
	return render_template("reportes.html",rdia=r_dia, rmes=r_mes, rano=r_ano)

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



if __name__ == "__main__":
    app.run(debug=True)
