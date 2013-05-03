import MySQLdb
import ConfigParser
import sys

cp = ConfigParser.ConfigParser()
cp.read("configuracion.ini")
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
		dbh.execute("insert into %s (estado,codigo, segmento) values (1,%s,%d)" % (table,elem_code,int(elem_seg)))
cn.commit()
dbh.close()