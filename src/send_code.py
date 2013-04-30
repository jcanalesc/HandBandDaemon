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

if len(sys.argv) > 1:
	for elem in sys.argv[1:]:
		print("sending code %s" % elem)
		dbh.execute("insert into pulseras (codigo) values (%s)", elem)

dbh.close()