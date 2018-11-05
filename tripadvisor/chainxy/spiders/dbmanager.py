import mysql.connector as sql
import os
from mysql.connector import errorcode
import pdb

dbConfig = {
	'user': 'root',
	'password': '',
	'database': 'tripadvisor'
}


def checkDBConnection():
	if dbConfig:
		try:
			cnx = sql.connect(**dbConfig)
			cursor = cnx.cursor()

			cursor.execute("SHOW TABLES")
			result = cursor.fetchall()

			if not result and os.path.exists('require/init_db.sql'):
				stmt = ''

				with open('require/init_db.sql', 'r') as f:
					stmt = f.read()

				results = cursor.execute(stmt, multi=True)

				for cur in results:
					print('cursor:', cur)
					if cur.with_rows:
						print('result:', cur.fetchall())

				if os.path.exists('require/init_COUNTRY_CODE_TO_COUNTRY_NAME_TABLE.sql'):
					with open('require/init_COUNTRY_CODE_TO_COUNTRY_NAME_TABLE.sql', 'r') as f:
						stmt = f.read()

					results = cursor.execute(stmt, multi=True)

					for cur in results:
						print('cursor:', cur)
						if cur.with_rows:
							print('result:', cur.fetchall())

				cnx.commit()

			cursor.close()
			cnx.close()

			return True
		except sql.Error as err:
			if err.errno == errorcode.ER_BAD_DB_ERROR:
				print 'Please create Database (%s)' % (dbConfig['database'])
			else:
				print err
	else:
		print 'Please set db configuration'

	return False


def isTableExisting(tablename=''):
	if dbConfig:
		cnx = sql.connect(**dbConfig)
		cursor = cnx.cursor()
		stmt = "SHOW TABLES LIKE '%s'" % (tablename)
		cursor.execute(stmt)
		result = cursor.fetchone()

		cursor.close()
		cnx.close()

		if not result:
			print '==========================================='
			print '==========================================='
			print '========= Table is not exsting ============'
			print tablename
			print '==========================================='
			print '==========================================='

		return True if result else False

	return False