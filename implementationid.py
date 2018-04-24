#!/usr/bin/python

# This python script is meant to be used with the implementationid module.
# It keeps a record of unique implementation id / passphrase pairs

from flask import Flask, request, abort
import sys
import optparse
import time, logging
import sys, MySQLdb, os, string, bcrypt

app = Flask(__name__) # create the application instance :)


def __getDatabaseConnection(db_host, db_name, db_user, db_passwd):
	return MySQLdb.connect(db_host, db_user, db_passwd, db_name)

def __logAccessAttempt(dbh, implementationId, success, request):
    ip = "LOCAL"
    if 'X-Forwarded-For' in request.headers:
	    ip = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        ip = request.remote_addr or 'untrackable'

	cursor = dbh.cursor()
	cursor.execute("""INSERT INTO access_log
					(ip_address, access_date, access_time, implementation_id, success)
					VALUES
					(%s, CURDATE(), CURTIME(), %s, %s)""",
					(ip, implementationId, success))

	cursor.close()
	dbh.commit()

@app.errorhandler(500)
def catch_server_errors(e):
    app.logger.error("Unexpected exception")
    app.logger.exception(e)

@app.route("/ping", methods=['GET'])
def ping():
	return 'Hello, World!\n'

@app.route("/tools/implementationid", methods=['POST'])
def post_implementation():

	implementationId = request.form["implementationId"]
	description = request.form["description"]
	passphrase = request.form["passphrase"]

	if implementationId == "" or description == "" or passphrase == "":
		abort(400, description='An error occurred while trying to read the implementation id, description, and pass phrase. All values are required.')
	elif '^' in implementationId or '|' in implementationId:
		abort(400, description="The implementation id contains the invalid character: '^|'")
	else:
		db_host = os.environ["DB_HOST"]
		db_user = os.environ["DB_USERNAME"]
		db_passwd = os.environ["DB_PASSWORD"]
		db_name = os.environ["DB_NAME"]

		dbh = __getDatabaseConnection(db_host, db_name, db_user, db_passwd)

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
			cursor = dbh.cursor();
			hashed_passphrase = bcrypt.hashpw(passphrase.encode('UTF_8'), bcrypt.gensalt())
			cursor.execute("INSERT INTO implementation_id (implementation_id, description, passphrase) VALUES (%s, %s, %s)",
							(implementationId, description, hashed_passphrase))
			cursor.close();
			dbh.commit();
			__logAccessAttempt(dbh, implementationId, 1, request)
			return 'Success creating ' +  description
		else:
			# there was a hit, check the passphrase against what was given
			if bcrypt.checkpw(passphrase.encode('UTF_8'), row[2]):
				__logAccessAttempt(dbh, implementationId, 1, request)
				return 'Success recovering ' + row[1]
			else:
				# invalid passphrase.  Just print the current description
				__logAccessAttempt(dbh, implementationId, 0, request)
				abort(403, description="Invalid implementationid or passphrase")


		# close connection and we're done
		dbh.close()


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python implementationid.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on.')
    (args, _) = parser.parse_args()
    if args.port == None:
        print "Missing required argument: -p/--port"
        sys.exit(1)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)
