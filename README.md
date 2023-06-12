<h1 align="center">Dockerized MySQL Replication 👋</h1>
<p>
  <a href="#" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
  <img alt="documentation: yes" src="https://img.shields.io/badge/Documentation-Yes-green.svg" />
  <img alt="maintained: yes" src="https://img.shields.io/badge/Maintained-Yes-green.svg" />
</p>

> This project explores the concept of Command Query Responsibility Segregation (CQRS) and demonstrates how to implement
> it by using Docker to containerize MySQL replication. The system utilizes a load-balancing technique to distribute the
> workload between multiple slave database servers for read operations, while maintaining a single master server for
> write
> operations.

### Configuration data
Please consider change the database credential, read only user will available in every slave database sever
```json
{
  "master": {
    "master_database_host": "master_db",
    "master_database_port": 3306,
    "master_database_root_user": "root",
    "master_database_root_password": "hh$fEt^LIr&IBKpBsHJsKZj5bmUp+(ta",
    "write_only_users": [
      {
        "write_only_username": "dev_01_master",
        "write_only_password": "h%FgaCR2ay#rNaY!Kn!cenQcJH&yDYWz",
        "write_only_databases": [
          "svc1db",
          "svc2db",
          "svc3db"
        ],
        "write_only_grant_types": [
          "INSERT",
          "UPDATE",
          "DELETE",
          "CREATE",
          "ALTER",
          "DROP"
        ]
      }
    ],
    "read_only_users": [
      {
        "read_only_username": "dev_01_slaves",
        "read_only_password": "vLUeHfFcC$jSe7!^MYqInUTXfd$j#z!$",
        "read_only_databases": [
          "svc1db",
          "svc2db",
          "svc3db"
        ],
        "read_only_grant_types": [
          "SELECT"
        ]
      }
    ],
    "slaves": [
      {
        "slave_database_host": "slave_db1",
        "slave_database_port": 3306,
        "slave_database_root_user": "root",
        "slave_database_root_password": "AJqa+heUHV(PmCJ35amnC^XcCacM8h6r",
        "slave_user": {
          "slave_db_user": "slave_user_db1",
          "slave_db_password": "Q)3RnhYHpzAeVN(8wjMJ#@wI*F8xkb4J"
        }
      },
      {
        "slave_database_host": "slave_db2",
        "slave_database_port": 3306,
        "slave_database_root_user": "root",
        "slave_database_root_password": "sT&9!AP7KJHC2J#4VFV$H53%WBRB5Wxq",
        "slave_user": {
          "slave_db_user": "slave_user_db2",
          "slave_db_password": "!W2F76YjLp7MjW$%vGatqwDP(^2eM+!)"
        }
      }
    ]
  }
}
```

### Docker-Compose Services Explanation

- **master_db**:
    - This service represents the master database. It is responsible for handling data entry (WRITE operations).
        - ```context : ./database/master/Dockerfile```
        - ```env : ./database/master/.master.env```
        - ```config : ./database/master/master.cnf```
        - ```port : 3311:3306```
        - ```network : network_db```
        - ```volume : database_data_master```

- **slave_db1**:
    - This service represents the first slave database. It is responsible for handling (READ operations).
        - ```context : ./database/slave/Dockerfile```
        - ```env : ./database/slave/.slave1.env```
        - ```config : ./database/slave/slave1.cnf```
        - ```network : network_db```
        - ```volume : database_data_slave1```

- **slave_db2**:
    - This service represents the second slave database. It is responsible for handling (READ operations).
        - ```context : ./database/slave/Dockerfile```
        - ```env : ./database/slave/.slave2.env```
        - ```config : ./database/slave/slave2.cnf```
        - ```network : network_db```
        - ```volume : database_data_slave2```

- **nginxlb**:
    - This service represents as a Nginx load balancer.
        - ```version : nginx:1.20.1```
        - ```config : ./nginxlb/nginx.conf```
        - ```port : 3310:3310```
        - ```network : network_db```

- **init**:
    - This service is responsible for initializing the database replication setup.
        - ```context : ./init/Dockerfile```
        - ```config : ./config.json```
        - ```network : network_db```

-----------------------------------------------

### Possible command Makefile

| Command                  | Description                                                                                                                                                                                                                                                                                                                                                                                                           |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| up                       | This command runs the `docker-compose up` command, which starts the services defined in the Docker Compose file.                                                                                                                                                                                                                                                                                                      |
| up-d                     | This command runs the `docker-compose up -d` command, which starts the services defined in the Docker Compose file in detached mode, allowing them to run in the background.                                                                                                                                                                                                                                          |
| ps                       | This command runs the `docker-compose ps` command, which lists the status of the containers defined in the Docker Compose file.                                                                                                                                                                                                                                                                                       |
| down                     | This command runs the `docker-compose down --remove-orphans` command, which stops and removes the containers, networks, and volumes defined in the Docker Compose file. The `--remove-orphans` flag ensures that any containers not defined in the Compose file are also removed.                                                                                                                                     |
| clean                    | This command cleans up the Docker environment by running multiple commands: `docker-compose down --remove-orphans` removes containers, networks, and volumes defined in the Docker Compose file, `docker volume rm` removes specific Docker volumes, and `docker rmi` removes specific Docker images.                                                                                                                 |
| master-root-cmd          | This command retrieves the host, root user, and root password from the `config.json` file and then executes a MySQL command inside the specified container. It allows executing commands as the root user on the master database.                                                                                                                                                                                     |
| master-wo-cmd            | This command retrieves the host, write-only username, and write-only password from the `config.json` file and then executes a MySQL command inside the specified container. It allows executing commands as the write-only user on the master database.                                                                                                                                                               |
| slave-root-cmd           | This command retrieves the appropriate slave host, root user, and root password from the `config.json` file based on the slave's ID (if available) and then executes a MySQL command inside the specified container. It allows executing commands as the root user on the slave database. If there are multiple slaves, it selects the appropriate host, root user, and root password based on the ID.                |
| slave-ro-cmd ID={}       | This command retrieves the appropriate slave host and read-only username and password from the `config.json` file based on the slave's ID (if available) and then executes a MySQL command inside the specified container. It allows executing commands as the read-only user on the slave database. If there are multiple slaves, it selects the appropriate host, read-only username, and password based on the ID. |
| master-env-generate      | This command generates the environment file for the master database by creating a new file or overwriting an existing one. It retrieves the master database's root password from the `config.json` file and writes it along with the `MYSQL_GROUP_REPLICATION=FORCE_PLUS_PERMANENT` configuration to the environment file.                                                                                            |
| slave-env-generate ID={} | This command generates the environment file for the slave database by creating a new file or overwriting an existing one. It retrieves the slave database's root password from the `config.json` file and writes it along with the `MYSQL_GROUP_REPLICATION=FORCE_PLUS_PERMANENT` configuration and password based on the ID to the environment file.                                                                 |

-----------------------------------------------

### Thank you

-----------------------------------------------

📚 Thank you for taking the time to explore this repository. We hope you found the information useful and insightful.

🤝 If you have any questions, feedback, or suggestions, please feel free to reach out. We appreciate hearing from you
and value your input.

⭐️ Remember to star this repository if you found it helpful. It helps us to know that our work is making a difference.

💻 Keep coding, keep learning, and keep pushing the boundaries of what's possible!

-----------------------------------------------
