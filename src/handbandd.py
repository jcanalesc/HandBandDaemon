#!/usr/bin/env python
# -*- coding: utf-8 -*-
# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python testdaemon.py start

#standard python libs
import logging
import time
import ConfigParser
import cups
import os
import Code128b

#third party libs
from daemon import runner
import MySQLdb

#WDIR="/usr/share/handbandd/"
WDIR="/home/jcanales/handband/src/"
CONFIGFILE="configuracion.ini"

class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/handbandd/handbandd.pid'
        self.pidfile_timeout = 5
        self.cfg = ConfigParser.ConfigParser()
        self.dbh = None
        self.cups_conn = cups.Connection()
        self.printer = None

    def generaImagen(barcode_img):
        lienzo = Image.new("1",(1710+780, 300), 1)
        w,h = barcode_img.size
        b = img.convert("1")
        achique = 0.66
        fact = (300.0*achique)/h
        b = b.resize((int(w*fact),int(h*fact)))
        w,h = b.size
        topm = (lienzo.size[1] - h)/2
        return lienzo.copy().paste(b, (0, topm, w, h+topm))


    def run(self):
        try:
            os.chdir(WDIR)


            logger.info("Demonio iniciado. CWD: %s" % (os.getcwd()))

            if len(self.cfg.read(CONFIGFILE)) == 0:
                raise Exception("Archivo de configuracion no encontrado.")

            logger.info("Archivo de configuración leído")

            host = self.cfg.get("Database", "Host")
            user = self.cfg.get("Database", "Username")
            pswd = self.cfg.get("Database", "Password")
            dbn = self.cfg.get("Database", "Dbname")

            self.dbh = MySQLdb.connect(host=host, user=user, passwd=pswd, db=dbn)

            logger.info("Conectado a la base de datos")

            printers = self.cups_conn.getPrinters()

            logger.info("Buscando impresoras")

            if len(printers) == 0:
                raise Exception("No hay impresoras instaladas en el sistema")

            for prt in printers:
                logger.info("Impresora encontrada: %s (%s)" % (prt, printers[prt]["device-uri"]))

            # seleccionar impresora de trabajo
            nombre = self.cfg.get("Settings","DefaultPrinter")

            self.printer = printers[nombre]

            logger.info("Seleccionando impresora %s" % (self.printer["printer-info"]))
            
            crs = self.dbh.cursor()

            while True:
                #Main code goes here ...
                #Note that logger level needs to be set to logging.DEBUG before this shows up in the logs
                # TODO:
                # 1. Conectarse a la base de datos, con datos de un archivo de configuracion
                # 2. Verificar la conexión a la impresora
                # 3. Hacer polling (cada 1 seg?) a la base de datos en busca de elementos con el estado "Vendido, no impreso"
                # 4. Generar un código y enviarlo a la impresora.

                lines = crs.execute("SELECT id, codigo FROM pulseras WHERE impreso = false")

                for row in crs.fetchall():

                    id_pulsera = row[0]
                    codigo_pulsera = row[1]

                    barcode = Code128b.code128_image(str(codigo_pulsera))

                    logger.info("Imprimiendo pulsera: %s - ID: %d" % (str(codigo_pulsera), id_pulsera))

                    # IMPRIMIR

                    img = generaImagen(barcode)

                    img.save("tmp/tmpfile_%s.png" % codigo_pulsera)

                    self.cups_conn.printFile(self.printer['printer-info'], "tmpfile.png","job_"+str(codigo_pulsera), 
                        {"media":"Custom.1x8.85in","orientation-requested":"4"})

                    crs.execute("UPDATE pulseras SET impreso = true WHERE id = %d" % (id_pulsera))

                    logger.info("Pulsera %s (ID: %d) impresa. Base de datos actualizada." % (str(codigo_pulsera), id_pulsera))

                time.sleep(1) # un segundo

        except ConfigParser.ParsingError as pe:
            logger.error("Archivo de configuración inexistente o inválido:")
        except MySQLdb.InterfaceError as ie:
            logger.error("La conexión a la base de datos falló")
        except MySQLdb.DatabaseError as de:
            logger.error("Ha ocurrido un error en la base de datos: %s" % (str(de)))
        except Exception as e:
            logger.error(e)
	logger.info("Finalizando")



app = App()
logger = logging.getLogger("Demonio HandBand")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/handbandd/handbandd.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()
