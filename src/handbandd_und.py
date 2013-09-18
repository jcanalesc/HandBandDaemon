#!/usr/bin/env python
# -*- coding: utf-8 -*-
#standard python libs
import logging
import time
import ConfigParser
import cups
import os
import Code128b
import subprocess
import glob
#third party libs
from daemon import runner
from PIL import Image, ImageDraw, ImageFont
import MySQLdb

#WDIR="/usr/share/handbandd/"
WDIR="/usr/share/handbandd/"
CONFIGFILE="configuracion.ini"

NO_HABILITADO = 0
HABILITADO_PARA_IMPRESION = 1
IMPRESO = 2

## TODO: agregar indicador si el estado de la impresora cambia (enchufada/desenchufada o encendida/apagada). 
## Recordarle al usuario que los trabajos se imprimirán cuando se restablezca la conexión.

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
        self.font = ImageFont.truetype(WDIR+"BebasNeue.otf", 80)
        self.font_debug = ImageFont.truetype(WDIR+"BebasNeue.otf", 40)
        self.font_web = ImageFont.truetype(WDIR+"BebasNeue.otf", 30)
        self.segmentos = []
        self.logo = {}
        self.s_printers = {}


    def generaImagen(self,barcode_img, segmento, fechaventa, debug=False):
        # TODO: Ordenar esta cosa

        lienzo = Image.new("1",(1710+780, 300), 1)

        imgweb = Image.new("1",(300,30), 1)

        drawer = ImageDraw.Draw(imgweb)

        margen = int((300 - self.font_web.getsize("www.handband.cl")[0]) / 2)

        drawer.text((margen,0), "www.handband.cl", font=self.font_web)

        imgweb2 = imgweb.rotate(90, expand=True).crop((1,0,31,300))
        imgweb2.load()
        imgweb = imgweb2

        lienzo.paste(imgweb, (0,0, 30, 300))

        w,h = barcode_img.size
        b = barcode_img.convert("1")
        achique = 0.66
        fact = (300.0*achique)/h
        b = b.resize((int(w*fact),int(h*fact)))
        w,h = b.size
        topm = (lienzo.size[1] - h)/2
        # pegar codigo de barras
        lienzo.paste(b, (30, topm, w+30, h+topm))
        # pegar asignacion (normal-pref-vip)
        asignacion = Image.new("1", (300,300), 1)
        drawer = ImageDraw.Draw(asignacion)

        tipo_asignacion = self.segmentos[segmento]

        alt = int((300 - 80)/2)
        drawer.text((0, alt), tipo_asignacion, font=self.font)

        lienzo.paste(asignacion,(30+w+10, 0, 30+w+310, 300))

        #pegar logo

        lienzo.paste(self.logo_img, (30+w+310+10, 0, 30+w+310+10+self.logo['w'], self.logo['h']))

        #pegar fechahora

        fechahora = Image.new("1", (400,300), 1)
        drawer = ImageDraw.Draw(fechahora)
        #drawer.text((0,20), "Emitido el", font=self.font)
        fechaventap = fechaventa.split(" ")
        alt = int((300 - 80*2)/2)
        drawer.text((0,alt), fechaventap[0], font=self.font)
        drawer.text((0,alt+80), fechaventap[1], font=self.font)

        lienzo.paste (fechahora, (30+w+310+10+self.logo['w']+10, 0, 30+w+310+10+self.logo['w']+10+400, 300))

        if debug != False:
            drawer = ImageDraw.Draw(lienzo)
            tam_w, tam_h = self.font_debug.getsize(debug)
            margen_izq = int((b.size[0] - tam_w) / 2) + 30
            margen_sup = int((b.size[1] + 10)) + topm
            drawer.text((margen_izq, margen_sup), debug, font=self.font_debug)

        return lienzo

    def connect_to_database(self):
        host = self.cfg.get("Database", "Host")
        user = self.cfg.get("Database", "Username")
        pswd = self.cfg.get("Database", "Password")
        dbn = self.cfg.get("Database", "Dbname")
        table = self.cfg.get("Database", "Tablename")

        tries = 5 # -1 para intentar infinitamente

        while (tries > 0 or tries == -1):
            try:
                self.dbh = MySQLdb.connect(host=host, user=user, passwd=pswd, db=dbn)
                return True
            except MySQLdb.InterfaceError as ie:
                logger.info("Fallo la conexion: %s" % str(ie))

            if tries > 1 or tries == -1:
                logger.info("Reintentando conexion en 10 segundos...")
            time.sleep(10)
            tries = tries - 1
        return False

    def run(self):
        try:
            os.chdir(WDIR)
            time.sleep(1)
            logger.info("Demonio iniciado. CWD: %s" % (os.getcwd()))

            logger.info("Limpiando carpeta temporal")
            files = glob.glob(WDIR+"tmp/*")
            for f in files:
                os.remove(f)

            if len(self.cfg.read(CONFIGFILE)) == 0:
                raise Exception("Archivo de configuracion no encontrado.")

            logger.info("Archivo de configuración leído")

            self.segmentos = self.cfg.get("Segment", "Options").split(",")

            self.logo['file'] = self.cfg.get("Logo", "File")
            self.logo['w'] = int(self.cfg.get("Logo", "Width"))
            self.logo['h'] = int(self.cfg.get("Logo", "Height"))

            self.logo_img = Image.open(self.logo['file']).convert("1")

            self.logo_img = self.logo_img.resize((self.logo['w'], self.logo['h']))
           
            printers = self.cups_conn.getPrinters()

            logger.info("Buscando impresoras")

            if len(printers) == 0:
                raise Exception("No hay impresoras instaladas en el sistema.")

            imp = []

            for prt in printers:
                imp.append(str(prt))
                logger.info("Impresora encontrada: %s (%s)" % (prt, printers[prt]["device-uri"]))
            # seleccionar impresora de trabajo

            def_printer = self.cfg.get("Printers", "Default")

            self.printer = printers[def_printer]

            logger.info("Seleccionando impresora predeterminada %s" % (self.printer["printer-info"]))
            if self.printer["printer-state"] not in [3,4]:
                logger.warning("La impresora \"%s\" no esta lista. Las pulseras quedaran encoladas hasta que la impresora este lista." % def_printer)

            for seg in self.segmentos:
                if seg != "General":
                    # Busco si el archivo de configuracion especifica impresoras para cada segmento especial
                    if self.cfg.has_option("Printers", seg):
                        sprt = self.cfg.get("Printers", seg)
                        if sprt in imp:
                            logger.info("Seleccionando impresora especial para segmento %s: %s" % (seg, sprt))
                            self.s_printers[seg] = sprt
                            if printers[sprt]['printer-state'] not in [3,4]:
                                logger.warning("La impresora \"%s\" no esta lista. Las pulseras quedaran encoladas hasta que la impresora este lista." % sprt)

            bthickness = int(self.cfg.get("Barcode", "Thickness"))
            bheight = int(self.cfg.get("Barcode", "Height"))

            table = self.cfg.get("Database", "Tablename")
            
            while True:
                conectado = self.connect_to_database()
                if not conectado:
                    raise Exception("No se logro realizar una conexion con la base de datos")
                crs = self.dbh.cursor()

                # TODO:
                # 1. Conectarse a la base de datos, con datos de un archivo de configuracion
                # 2. Verificar la conexión a la impresora
                # 3. Hacer polling (cada 1 seg?) a la base de datos en busca de elementos con el estado "Vendido, no impreso"
                # 4. Generar un código y enviarlo a la impresora.
                # logger.info("SELECT id, codigo FROM `%s` WHERE estado = 0" % (table))
                
                lines = crs.execute("SELECT id, codigo, segmento,fecha_venta  FROM `%s` WHERE estado = %d" % (table, HABILITADO_PARA_IMPRESION))
                for row in crs.fetchall():

                    """
                    Problema:
                    Multiples peticiones de impresión rápidas hacían que la impresora enviara pulseras en blanco. Posible problema con
                    el driver USB.
                    Solucion:
                    Reiniciar el dispositivo USB.
                    """
                    #subprocess.call(["usb_modeswitch -R -v 0a5f -p 008b > /dev/null"], shell=True)

                    id_pulsera = row[0]
                    codigo_pulsera = row[1]
                    segmento = int(row[2])
                    fechaventa = row[3]

                    impresora_objetivo = def_printer
                    if self.segmentos[segmento] in self.s_printers:
                        impresora_objetivo = self.s_printers[self.segmentos[segmento]]


                    barcode = Code128b.code128_image(str(codigo_pulsera), bheight, bthickness)

                    logger.info("Imprimiendo pulsera: %s - ID: %d Segmento: %s " % (str(codigo_pulsera), id_pulsera, self.segmentos[segmento]))

                    # IMPRIMIR
                    if codigo_pulsera[0] == "D":
                        img = self.generaImagen(barcode, segmento, str(fechaventa), codigo_pulsera)
                    else:
                        img = self.generaImagen(barcode, segmento, str(fechaventa))

                    rutaarchivo = os.getcwd() + "/tmp/tmpfile_%s.png" % codigo_pulsera

                    img.save(rutaarchivo)

                    logger.info("Enviando archivo %s" % rutaarchivo)
                    res = self.cups_conn.printFile(impresora_objetivo,
                             rutaarchivo,
                            "job_"+str(codigo_pulsera)+time.strftime("%Y%m%d%H%M%S"), 
                            {"media":"Custom.1x8.85in","orientation-requested":"4"})

                    logger.info("[cups]: %s", str(res))
                    
                    crs.execute("UPDATE `%s` SET estado = %d WHERE id = %d" % (table, IMPRESO,  id_pulsera))

                    estado_imp = self.cups_conn.getPrinterAttributes(name=impresora_objetivo, requested_attributes=['printer-state'])
                    
                    if estado_imp['printer-state'] not in [3,4]:
                        logger.info("Pulsera %s (ID: %d) (Segmento: %s) encolada para impresion. Se imprimira cuando la impresora este lista. Base de datos actualizada." % (str(codigo_pulsera), id_pulsera, self.segmentos[segmento]))
                    else:
                        logger.info("Pulsera %s (ID: %d) (Segmento: %s) impresa. Base de datos actualizada." % (str(codigo_pulsera), id_pulsera, self.segmentos[segmento]))

                self.dbh.commit()
                crs.close()
                self.dbh.close()
                time.sleep(1) # un segundo

        except ConfigParser.ParsingError as pe:
            logger.error("Archivo de configuración inexistente o inválido:")
        except MySQLdb.InterfaceError as ie:
            logger.error("La conexión a la base de datos falló")
        except MySQLdb.DatabaseError as de:
            logger.error("Ha ocurrido un error en la base de datos: %s" % (str(de)))
        except Exception as e:
            logger.error(e.__class__.__name__ +":"+ str(e))
	logger.info("Finalizando")


if __name__ == "__main__":
    app = App()
    logger = logging.getLogger("Demonio HandBand")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler("/var/log/handbandd/handbandd.log")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    app.run()
    exit(1)
    
