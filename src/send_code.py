import MySQLdb
import ConfigParser
import sys
import random


cp = ConfigParser.ConfigParser()
cp.read("/usr/share/handbandd/configuracion.ini")
cn =  MySQLdb.connect(host=cp.get("Database", "Host"),
					  user=cp.get("Database", "Username"),
					  passwd=cp.get("Database", "Password"),
					  db=cp.get("Database", "Dbname"))
dbh = cn.cursor()

table = cp.get("Database", "Tablename")

if len(sys.argv) > 1:
	for elem in sys.argv[1:]:
		elem_code, elem_seg = elem.split(":")
		print("sending code %s" % elem)
		dbh.execute("insert into %s (estado,codigo, segmento) values (1,'%s',%d)" % (table,elem_code,int(elem_seg)))
else:
	dbh.execute("insert into %s (estado,codigo, segmento) values (1,'%s',%d)" % (table,str(random.randint(100000,999999)),int(0)))
cn.commit()
dbh.close()