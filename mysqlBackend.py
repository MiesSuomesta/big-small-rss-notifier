
import mysql.connector as MYCN
from loginmanager import *

class MySQLBackend:

	def __init__(self):

		self.login = config_get_data("mysql")

		self.mysql_conn = None

	def mysql_connect(self):
		""" Connect to MySQL database """
		self.mysql_conn = None
		try:
			self.mysql_conn = MYCN.connect(host='localhost',
						database='kauppalehtiOsakkeet',
						user=self.login['username'],
						password=self.login['password'])

		except Error as e:
			if self.mysql_conn is not None and self.mysql_conn.is_connected():
				self.mysql_conn.close()
			print(e)

		return self.mysql_conn


	def palauta_kaikki_arvopaperin_kirjaukset(self, arvopaperin_nimi):

		record = None
		try:

			cursor = self.pre_mysql()

			query = 'select * from osakedata where Osake = "{}"'.format(arvopaperin_nimi)
			
			cursor.execute(query, ())
			record = cursor.fetchall()

			#print("query", query )
			#print("recordit", record )

			self.post_mysql(cursor)

		except Error as error:
			if self.mysql_conn is not None and self.mysql_conn.is_connected():
				self.mysql_conn.close()

			traceback.print_exc(file=sys.stdout)
			print(error)
			cursor = None

		return record

	def palauta_kaikki_arvopaperien_nimet(self):

		record = None

		cursor = self.pre_mysql()

		query = 'select distinct Osake from osakedata;'
		cursor.execute(query, ())
		record = cursor.fetchall()

		nimilista = []
		for row in record:
			nimi = row[0]

			if nimi not in nimilista:
				#print("Adding nimi {}".format(nimi))
				nimilista.append(nimi)

		self.post_mysql(cursor)

		return nimilista



	def pre_mysql(self):

		cursor = None

		try:
			if self.mysql_conn is None:
				self.mysql_conn = self.mysql_connect()

			cursor = self.mysql_conn.cursor()

		except Error as error:
			if self.mysql_conn is not None and self.mysql_conn.is_connected():
				self.mysql_conn.close()

			traceback.print_exc(file=sys.stdout)
			print(error)
			cursor = None

		return cursor

	def post_mysql(self, cursor):


		cursor.close()
		self.mysql_conn.close()
		self.mysql_conn = None;


	def palauta_kaikki_kannasta(self):

		record = None

		cursor = self.pre_mysql(cursor)

		query = 'select * from osakedata'
		cursor.execute(query, ())
		record = cursor.fetchall()

		self.post_mysql(cursor)

		return record


	def lisaa_osake_kantaan(self, osakeObjecti):
## ID BIGINT PRIMARY KEY AUTO_INCREMENT, Osake TINYTEXT, Paivays DATE, Hinta FLOAT, Muutos FLOAT, Osto FLOAT, Myynti FLOAT, Vaihto BIGINT , Ylin FLOAT, Alin FLOAT, Suositus TEXT


		try:
			if self.mysql_conn is None:
				self.mysql_conn = self.mysql_connect()

			cursor = self.mysql_conn.cursor()


			query = 'INSERT INTO osakedata(Id, Osake, Paivays, Hinta, Muutos, Osto, Myynti, Vaihto, Ylin, Alin, Suositus) VALUES(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


			args = (	cursor.lastrowid,		# %s
					osakeObjecti.Osake,		# %s
					osakeObjecti.Paivays,		# %s
					osakeObjecti.Hinta,		# %s
					osakeObjecti.Muutos,		# %s
					osakeObjecti.Osto,		# %s
					osakeObjecti.Myynti,		# %s
					osakeObjecti.Vaihto,		# %s
					osakeObjecti.Ylin,		# %s
					osakeObjecti.Alin,		# %s
					osakeObjecti.Suositus )		# %s


			cursor.execute(query, args)

			self.mysql_conn.commit()

		except Error as error:
			if self.mysql_conn is not None and self.mysql_conn.is_connected():
				self.mysql_conn.close()

			traceback.print_exc(file=sys.stdout)
			print(error)

		finally:
			cursor.close()
			self.mysql_conn.close()
			self.mysql_conn = None;

