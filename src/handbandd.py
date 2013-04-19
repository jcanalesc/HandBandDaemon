#!/usr/bin/env python
# -*- coding: utf-8 -*-
# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python testdaemon.py start

#standard python libs
import logging
import time
import ConfigParser
import MySQLdb
#third party libs
from daemon import runner


CONFIGFILE="configuracion.ini"

class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/handhandd/handbandd.pid'
        self.pidfile_timeout = 5
        self.cfg = ConfigParser.ConfigParser()
        self.dbh = None    
    def run(self):

        try:
            self.cfg.read(CONFIGFILE)

            host = self.cfg.get("Database", "Host")
            user = self.cfg.get("Database", "Username")
            pswd = self.cfg.get("Database", "Password")
            dbn = self.cfg.get("Database", "Dbname")

            self.dbh = MySQLdb.connect(host=host, user=user, passwd=pswd, db=dbn)

            logger.info("Conectado a la base de datos")
            
            crs = self.dbh.cursor()

            while True:
                #Main code goes here ...
                #Note that logger level needs to be set to logging.DEBUG before this shows up in the logs
                # TODO:
                # 1. Conectarse a la base de datos, con datos de un archivo de configuracion
                # 2. Verificar la conexión a la impresora
                # 3. Hacer polling (cada 1 seg?) a la base de datos en busca de elementos con el estado "Vendido, no impreso"
                # 4. Generar un código y enviarlo a la impresora.
                crs.execute("SELECT id, codigo FROM pulseras WHERE impreso = false");
                for row in crs.fetchall():
                    id_pulsera = row[0]
                    codigo_pulsera = row[1]


                time.sleep(0.5) # Medio segundo de espera entre polls

        except ConfigParser.ParsingError as pe:
            logger.error("Archivo de configuración inexistente o inválido:")
        except MySQLdb.InterfaceError as ie:
            logger.error("La conexión a la base de datos falló")
        except MySQLdb.DatabaseError as de:
            logger.error("Ha ocurrido un error en la base de datos")
        except Exception as e:
            logger.error("Error desconocido.")

app = App()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/handbandd/handbandd.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()
