
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
						database='uutisetRss',
						user=self.login['username'],
						password=self.login['password'])

		except Error as e:
			if self.mysql_conn is not None and self.mysql_conn.is_connected():
				self.mysql_conn.close()
			print(e)

		return self.mysql_conn

	def palauta_kannasta(self, Osake = None, Paivays = None, Hinta = None, Muutos = None, Osto = None, Myynti = None, 
					Vaihto = None, Ylin = None, Alin = None, Suositus = None):

		def add_str_for(cName, mName):
			return '{} = "{}"'.format(cName, mName)
			 
		record = None

		try:
			if self.mysql_conn is None:
				self.mysql_conn = self.mysql_connect()

			cursor = self.mysql_conn.cursor()

			
			select_str = "*"
			add_where = False
			WHERE_ADD = ""
			if Osake is not None:
				WHERE_ADD = WHERE_ADD + add_str_for('Osake', Osake)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Paivays is not None:
				WHERE_ADD = WHERE_ADD +add_str_for('Paivays', Paivays)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Hinta is not None:
				WHERE_ADD = WHERE_ADD +add_str_for('Hinta', Hinta)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Muutos is not None:
				WHERE_ADD = WHERE_ADD +add_str_for('Muutos', Muutos)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Osto is not None:
				WHERE_ADD = WHERE_ADD +add_str_for('Osto', Osto)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Myynti is not None:
				WHERE_ADD = WHERE_ADD +add_str_for('Myynti', Myynti)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Vaihto is not None:
				WHERE_ADD = WHERE_ADD +add_str_for('Vaihto', Vaihto)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Ylin is not None:
				WHERE_ADD = WHERE_ADD +add_str_for('Ylin', Ylin)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Alin is not None:
				WHERE_ADD = WHERE_ADD +add_str_for('Alin', Alin)
				WHERE_ADD = WHERE_ADD + " and "
				add_where = True
			if Suositus is not None:
				add_str_for('Suositus', Suositus)
				add_where = True

			if add_where:
				WHERE_ADD = "where " + WHERE_ADD


				
			query = 'select * from osakedata {}'.format(WHERE_ADD)
			print ("Query: ", query)
			cursor.execute(query, ())

			record = cursor.fetchall()


		except Error as error:
			if self.mysql_conn is not None and self.mysql_conn.is_connected():
				self.mysql_conn.close()

			traceback.print_exc(file=sys.stdout)
			print(error)

		finally:
			cursor.close()
			self.mysql_conn.close()
			self.mysql_conn = None;

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

