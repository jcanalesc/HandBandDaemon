import sys
from flask import Flask, render_template, jsonify
import bdd
import subprocess
import os
import random
app = Flask(__name__)

@app.route("/")
def main():
    return render_template("main.html")

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
		bdd.agregar()
		return jsonify({"res": True})
	except Exception as e:
		return jsonify({"res": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)