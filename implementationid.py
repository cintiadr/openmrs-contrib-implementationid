#!/usr/bin/python

# This python script is meant to be used with the implementationid module.
# It keeps a record of unique implementation id / passphrase pairs

def getDatabaseConnection():
	return MySQLdb.connect(host='localhost',
				user='implid_user', passwd='PASSWORD', 
				db="implementationid")

def printStatusOk():
	print 'Status: 200 Ok'
	print 'Content-Type: text/plain\n\n'

def printStatusError():
	print 'Status: 400 Bad Request'
	print 'Content-Type: text/plain\n\n'

# logs this IP address's attempt at this implementationId
# returns the number of attempts by this ip address today
def logAccessAttempt(dbh, implementationId, passphrase, success):
	ip = "LOCAL"
	if (os.environ.has_key("REMOTE_ADDR")):
		ip = os.environ["REMOTE_ADDR"]

	cursor = dbh.cursor()

	cursor.execute("""INSERT INTO access_log
					(ip_address, access_date, access_time, implementation_id, passphrase, success)
					VALUES
					(%s, CURDATE(), CURTIME(), %s, %s, %s)""",
					(ip, implementationId, passphrase, success))

	cursor.close()

	dbh.commit()

def unsuccessfulAttemptCount(dbh):
	ip = "LOCAL"
	if (os.environ.has_key("REMOTE_ADDR")):
		ip = os.environ["REMOTE_ADDR"]
	cursor = dbh.cursor()

	cursor.execute("""SELECT
						count(*)
					FROM
						access_log
					WHERE
						ip_address = %s AND
						access_date = CURDATE() AND
						success = 0
					""", (ip,))
	count = cursor.fetchone()[0]

	cursor.close()

	return count

import sys, cgi, MySQLdb, os, string

# store query parameters in fs
fs = cgi.FieldStorage()

# fetch the query parameters we're interested in
implementationId = fs.getvalue("implementationId", "")
description = fs.getvalue("description", "")
passphrase = fs.getvalue("passphrase", "")

if implementationId == "" or description == "" or passphrase == "":
	printStatusError()
	print 'An error occurred while trying to read the implementation id, description, and pass phrase. All values are required.'
else:
	# set up the database connection
	dbh = getDatabaseConnection()

	try:
		# get the number of miss hits
		attempts = unsuccessfulAttemptCount(dbh)

		if attempts >= 100:
			printStatusError()
			print "Invalid number of connection attempts.  Try again tomorrow."

		elif string.find(implementationId, "^") > -1:
			printStatusError()
			print "The implementation id contains the invalid character: '^'"

		elif string.find(implementationId, "|") > -1:
			printStatusError()
			print "The implementation id contains the invalid character: '|'"

		else:
			printStatusOk()

			cursor=dbh.cursor()
			cursor.execute("""
					SELECT
						implementation_id,
						description,
						passphrase
					FROM
						implementation_id
					WHERE
						implementation_id = %s """, (implementationId,))

			row = cursor.fetchone()
			cursor.close();

			# no row was found with this implementation id.  they are unique.  insert them into the database
			if row == None:
				logAccessAttempt(dbh, implementationId, passphrase, 1)
				cursor = dbh.cursor();
				cursor.execute("INSERT INTO implementation_id (implementation_id, description, passphrase) VALUES (%s, %s, %s)",
								(implementationId, description, passphrase))
				cursor.close();
				dbh.commit();

				print 'Success'
				print description

			else:
				# there was a hit, check the passphrase against what was given
				if row[2] == passphrase:
					logAccessAttempt(dbh, implementationId, passphrase, 1)
					print 'Success'
					print row[1]
				else:
					# invalid passphrase.  Just print the current description
					print row[1]
					logAccessAttempt(dbh, implementationId, passphrase, 0)

	except Exception, e:
		printStatusError()
		print "uh oh, got a python error:"
		print e

	# close connection and we're done
	dbh.close()
