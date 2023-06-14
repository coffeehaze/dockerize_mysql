import sys
import json
import pymysql

Q_PING = "SELECT 1"
Q_CREATE_DATABASE = "CREATE DATABASE IF NOT EXISTS `{}`"
Q_CREATE_USER = "CREATE USER '{}'@'%' IDENTIFIED BY '{}'"
Q_GRANT_REPLICATION_ON_SLAVE = "GRANT REPLICATION SLAVE ON *.* TO '{}'@'%'"
Q_GRANT_SELECT_ON = "GRANT SELECT ON *.* TO '{}'@'%'"
Q_FLUSH_PRIVILEGES = "FLUSH PRIVILEGES"
Q_CHANGE_MASTER = "CHANGE MASTER TO " \
                  "MASTER_HOST='{}', " \
                  "MASTER_USER='{}', " \
                  "MASTER_PASSWORD='{}', " \
                  "MASTER_LOG_FILE='{}', " \
                  "MASTER_LOG_POS={}"
Q_START_SLAVE = "START SLAVE"
Q_SHOW_SLAVE_STATUS = "SHOW SLAVE STATUS"
Q_SHOW_MASTER_STATUS = "SHOW MASTER STATUS"


def error_print(e):
    error_code, error_message = e.args
    print(f"[Error] {error_code} - {error_message}")


def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data


class Master:
    c = None
    cpos = None
    clog = None

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        db = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
        )
        self.c = db.cursor()

    def create_user(self, username, password):
        query = Q_CREATE_USER.format(username, password)
        print("*", query)
        try:
            self.c.execute(query)
            print("+", query)
        except Exception as e:
            error_print(e)

    def create_database(self, name):
        query = Q_CREATE_DATABASE.format(name)
        print("*", query)
        try:
            self.c.execute(query)
            print("+", query)
        except Exception as e:
            error_print(e)

    def grant_privilege_slave(self, username):
        query = Q_GRANT_REPLICATION_ON_SLAVE.format(username)
        print("*", query)
        try:
            self.c.execute(query)
            print("+", query)
        except Exception as e:
            error_print(e)

    def grant_privilege_select(self, username):
        query = Q_GRANT_SELECT_ON.format(username)
        print("*", query)
        try:
            self.c.execute(query)
            print("+", query)
        except Exception as e:
            error_print(e)

    def flush_privilege(self):
        query = Q_FLUSH_PRIVILEGES
        print("*", query)
        try:
            self.c.execute(query)
            print("+", query)
        except Exception as e:
            error_print(e)

    def status(self):
        query = Q_SHOW_MASTER_STATUS
        print("*", query)
        try:
            self.c.execute(query)
            ms_status = self.c.fetchone()
            self.clog = ms_status[0]
            self.cpos = ms_status[1]
            print("+", query)
        except Exception as e:
            error_print(e)


class Slave:
    c = None

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        db = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
        )
        self.c = db.cursor()

    def change_master(self, host, user, password, clog, cpos):
        query = Q_CHANGE_MASTER.format(host, user, password, clog, cpos)
        print("*", query)
        try:
            self.c.execute(query)
            print("+", query)
        except Exception as e:
            error_print(e)

    def start_slave(self):
        query = Q_START_SLAVE
        print("*", query)
        try:
            self.c.execute(query)
            print("+", query)
        except Exception as e:
            error_print(e)

    def status(self):
        query = Q_SHOW_SLAVE_STATUS
        print("*", query)
        try:
            self.c.execute(query)
            status = self.c.fetchall()
            columns = [column[0] for column in self.c.description]
            slave_status_data = []
            for row in status:
                row_data = dict(zip(columns, row))
                slave_status_data.append(row_data)
            json_data = json.dumps(slave_status_data, indent=4)
            print(json_data)
        except pymysql.err.OperationalError as error:
            error_code, error_message = error.args
            print(f"Error executing query: {error_code} - {error_message}")


def entry():
    json_data = read_json("config.json")
    master_host = json_data['master']['master_database_host']
    master_port = json_data['master']['master_database_port']
    master_root_user = json_data['master']['master_database_root_user']
    master_root_password = json_data['master']['master_database_root_password']

    master = Master(
        host=master_host,
        port=master_port,
        username=master_root_user,
        password=master_root_password,
    )

    slaves = json_data['master']['slaves']
    for s in slaves:
        slave_user = s['slave_user']['slave_db_user']
        slave_password = s['slave_user']['slave_db_password']
        master.create_user(username=slave_user, password=slave_password)
        master.grant_privilege_slave(username=slave_user)
        master.flush_privilege()

        slave_port = s['slave_database_port']
        slave_host = s['slave_database_host']
        slave_root_user = s['slave_database_root_user']
        slave_root_password = s['slave_database_root_password']

        slave = Slave(
            host=slave_host,
            port=slave_port,
            username=slave_root_user,
            password=slave_root_password,
        )

        master.status()
        slave.change_master(
            host=master_host,
            user=master_root_user,
            password=master_root_password,
            clog=master.clog,
            cpos=master.cpos,
        )
        slave.start_slave()
        slave.status()

    for ro_user in json_data['master']['read_only_users']:
        ro_username = ro_user["read_only_username"]
        ro_password = ro_user["read_only_password"]
        master.create_user(username=ro_username, password=ro_password)
        for database_name in ro_user["read_only_databases"]:
            master.create_database(database_name)
            master.grant_privilege_select(username=ro_username)
            master.flush_privilege()


if __name__ == '__main__':
    try:
        entry()
    except Exception as err:
        raise Exception("error occurred. This might be because the database servers are not ready yet.")
    print("All Good.")
    sys.exit(0)
