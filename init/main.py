import sys
import json
import pymysql

'''
additional function utility both intent usage
for master and slave cursor database
'''


def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data


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
    except pymysql.Error as error:
        print(f"Unable to connect to database: {error}")


def master_status(c):
    show_master_status_query = "SHOW MASTER STATUS"
    c.execute(show_master_status_query)
    ms_status = c.fetchone()
    current_log = ms_status[0]
    current_pos = ms_status[1]
    return current_log, current_pos


'''
these function intended to executed from master / slave root cursor
this is slave user preparation for each slaves database server
and can be use too for create slave read only user
'''


def create_user(c, user, password):
    create_user_query = "CREATE USER %s@'%%' IDENTIFIED BY %s"
    try:
        c.execute(create_user_query, (user, password))
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"{error_code} - {error_message}")
        print(f"This slave {user} its already created")

def create_user_to_host(c, user, password):
    create_user_query = "CREATE USER {}@'%' IDENTIFIED BY '{}'"
    try:
        c.execute(create_user_query.format(user, password))
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"{error_code} - {error_message}")

def create_database_if_not_exist(c, database_name):
    create_database_query = "CREATE DATABASE IF NOT EXISTS `{}`"
    try:
        c.execute(create_database_query.format(database_name))
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"Error executing query: {error_code} - {error_message}")

def grant_read_privilege_user(c, user):
    grant_privileges_query = "GRANT SELECT ON *.* TO %s@'%%'"
    try:
        c.execute(grant_privileges_query, (user,))
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"Error executing query: {error_code} - {error_message}")

def grant_privilege_user(c, user):
    grant_privileges_query = "GRANT REPLICATION SLAVE ON *.* TO %s@'%%'"
    try:
        c.execute(grant_privileges_query, (user,))
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"Error executing query: {error_code} - {error_message}")


def flush_privilege_user(c):
    flush_privileges_query = "FLUSH PRIVILEGES"
    try:
        c.execute(flush_privileges_query)
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"Error executing query: {error_code} - {error_message}")


'''
these function intended to executed from slave cursor
this is slave database user registration and slaves starter
'''


def change_master(c, master_host, user, password, clog, cpos):
    change_master_query = "CHANGE MASTER TO MASTER_HOST=%s, MASTER_USER=%s, MASTER_PASSWORD=%s, MASTER_LOG_FILE=%s, " \
                          "MASTER_LOG_POS=%s "
    try:
        c.execute(change_master_query, (master_host, user, password, clog, cpos))
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"Error executing query: {error_code} - {error_message}")


def start_slave(c):
    start_slave_query = "START SLAVE"
    try:
        c.execute(start_slave_query)
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"Error executing query: {error_code} - {error_message}")


def slave_status(c):
    show_slave_status_query = "SHOW SLAVE STATUS"
    try:
        c.execute(show_slave_status_query)
        status = c.fetchall()
        columns = [column[0] for column in c.description]
        slave_status_data = []
        for row in status:
            row_data = dict(zip(columns, row))
            slave_status_data.append(row_data)
        json_data = json.dumps(slave_status_data, indent=4)
        print(json_data)
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"Error executing query: {error_code} - {error_message}")

def test(c, user):
    grant_privileges_query = "GRANT CREATE USER ON *.* TO {}@'%'"
    flush_privileges_query = "FLUSH PRIVILEGES"
    try:
        c.execute(grant_privileges_query.format(user))
        c.execute(flush_privileges_query)
    except pymysql.err.OperationalError as error:
        error_code, error_message = error.args
        print(f"Error executing query: {error_code} - {error_message}")


def entry():
    json_data = read_json("config.json")

    master_host = json_data['master']['master_database_host']
    master_port = json_data['master']['master_database_port']
    master_root_user = json_data['master']['master_database_root_user']
    master_root_password = json_data['master']['master_database_root_password']

    master_cursor = connector(master_root_user, master_root_password, master_host, master_port)
    test(master_cursor, master_root_user)
    ping(master_cursor)

    slaves = json_data['master']['slaves']
    for slave in slaves:
        # slave user and password
        slave_port = slave['slave_database_port']
        slave_host = slave['slave_database_host']
        slave_root_user = slave['slave_database_root_user']
        slave_root_password = slave['slave_database_root_password']
        slave_user = slave['slave_user']['slave_db_user']
        slave_password = slave['slave_user']['slave_db_password']

        create_user(master_cursor, slave_user, slave_password)
        grant_privilege_user(master_cursor, slave_user)
        flush_privilege_user(master_cursor)

        slave_cursor = connector(slave_root_user, slave_root_password, slave_host, slave_port)
        (clog, cpos) = master_status(master_cursor)
        change_master(slave_cursor, master_host, master_root_user, master_root_password, clog, cpos)
        start_slave(slave_cursor)
        slave_status(slave_cursor)

        for ro_user in json_data['master']['slave_read_only_users']:
            ro_user_name = ro_user["slave_read_only_username"]
            ro_user_pasw = ro_user["slave_read_only_password"]
            create_user_to_host(master_cursor, ro_user_name, ro_user_pasw)
            for db in ro_user["slave_read_only_to_databases"]:
                create_database_if_not_exist(master_cursor, db)
                grant_read_privilege_user(master_cursor, ro_user_name)
            flush_privilege_user(master_cursor)

    master_status(master_cursor)


if __name__ == '__main__':
    try:
        entry()
    except Exception as err:
        raise Exception("error occurred. This might be because the database servers are not ready yet.")
    print("Master-Slave Initialization proces done.")
    print("Script Terminated.")
    sys.exit(0)
