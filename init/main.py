import sys
import time
import json
import pymysql

'''
additional function utility both intent usage
for master and slave cursor database
'''
def connector(user, password, host, port):
  db = pymysql.connect(
      host=host,
      port=port,
      user=user,
      password=password,
  )
  db_cursor = db.cursor()
  return db_cursor

def ping(cursor):
  try:
      cursor.execute("SELECT 1")
      cursor.fetchone()
      print("Database connection is active.")
  except pymysql.Error as err:
      print(f"Unable to connect to database: {err}")

def master_status(c):
  show_master_status_query = "SHOW MASTER STATUS"
  c.execute(show_master_status_query)
  ms_status = c.fetchone()
  current_log = ms_status[0]
  current_pos = ms_status[1]
  return (current_log, current_pos)

'''
these function intended to executed from master cursor
this is slave user preparation for each slaves database server
'''
def create_slave_user(c, user, password):
  create_user_query = "CREATE USER %s@'%%' IDENTIFIED BY %s"
  try:
    c.execute(create_user_query, (user, password))
  except pymysql.err.OperationalError as err:
    error_code, error_message = err.args
    print(f"This slave {user} its already created")

def grant_privilege_slave_user(c, user):
  grant_privileges_query = "GRANT REPLICATION SLAVE ON *.* TO %s@'%%'"
  try:
    c.execute(grant_privileges_query, (user,))
  except pymysql.err.OperationalError as err:
    error_code, error_message = err.args
    print(f"Error executing query: {error_code} - {error_message}")

def flush_privilege_slave_user(c):
  flush_privileges_query = "FLUSH PRIVILEGES"
  try:
    c.execute(flush_privileges_query)
  except pymysql.err.OperationalError as err:
    error_code, error_message = err.args
    print(f"Error executing query: {error_code} - {error_message}")

'''
these function intended to executed from slave cursor
this is slave database user registration and slaves starter
'''
def change_master(c, master_host, user, password, clog, cpos):
  change_master_query = "CHANGE MASTER TO MASTER_HOST=%s, MASTER_USER=%s, MASTER_PASSWORD=%s, MASTER_LOG_FILE=%s, MASTER_LOG_POS=%s"
  try:
    c.execute(change_master_query, (master_host, user, password, clog, cpos))
  except pymysql.err.OperationalError as err:
    error_code, error_message = err.args
    print(f"Error executing query: {error_code} - {error_message}")
def start_slave(c):
  start_slave_query = "START SLAVE"
  try:
    c.execute(start_slave_query)
  except pymysql.err.OperationalError as err:
    error_code, error_message = err.args
    print(f"Error executing query: {error_code} - {error_message}")
def slave_status(c):
  show_slave_status_query = "SHOW SLAVE STATUS"
  try:
    c.execute(show_slave_status_query)
    slave_status = c.fetchall()
    columns = [column[0] for column in c.description]
    slave_status_data = []
    for row in slave_status:
        row_data = dict(zip(columns, row))
        slave_status_data.append(row_data)
    json_data = json.dumps(slave_status_data, indent=4)
    print(json_data)
  except pymysql.err.OperationalError as err:
    error_code, error_message = err.args
    print(f"Error executing query: {error_code} - {error_message}")

def entry():
  master_host="master_db"
  master_port=3306
  master_root_user="root"
  master_root_password="MasterPassword"

  slaves = [
    {
      "port": 3306,
      "slave_db_user": 'mydb_slave_user',
      "slave_db_password": 'mydb_slave_pwd',
      "slave_host":"slave_db",
      "slave_root_user":"root",
      "slave_root_password":"SlavePassword"
    }
  ]
  master_cursor = connector(
    master_root_user, 
    master_root_password, 
    master_host, 
    master_port,
  )

  ping(master_cursor)
  for slave in slaves:
    # slave user and password
    slave_db_user=slave['slave_db_user']
    slave_db_password=slave['slave_db_password']
    port=slave['port']
    slave_host=slave['slave_host']
    slave_root_user=slave['slave_root_user']
    slave_root_password=slave['slave_root_password']

    create_slave_user(master_cursor, slave_db_user, slave_db_password)
    grant_privilege_slave_user(master_cursor, slave_db_user)
    flush_privilege_slave_user(master_cursor)

    slave_cursor = connector(slave_root_user, slave_root_password, slave_host, port)
    (clog, cpos) = master_status(master_cursor)
    change_master(slave_cursor, master_host, master_root_user, master_root_password, clog, cpos)
    start_slave(slave_cursor)
    slave_status(slave_cursor)
    
  master_status(master_cursor)

if __name__ == '__main__':
  try:
    entry()
  except Exception as err:
    raise Exception(f"{err} error occurred. This might be because the database servers are not ready yet.")
  print("All Good. Exiting with sys status 0...")
  print("Terminated...")
  sys.exit(0)
