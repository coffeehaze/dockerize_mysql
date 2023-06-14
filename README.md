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
> workload between multiple slave database servers for read operations, while maintaining a single master server for write
> operations.

### Docker-Compose Services Explanation
Here are the explanations for each service in the provided `docker-compose.yml` file:

- **master_db**: This service represents the master database. It is responsible for handling data entry (WRITE operations). It is built using the Dockerfile in the `./database/master` directory. It has its own environment file at `./database/master/.env` and is exposed on port `3311`. It is connected to the `network_db` network and has two volumes for data persistence: `database_data_master` and `./database/master/master.cnf` for the MySQL configuration file.

- **slave_db1**: This service represents the first slave database. It is responsible for handling read operations. It is built using the Dockerfile in the `./database/slave` directory. It has its own environment file at `./database/slave/.env`. It is connected to the `network_db` network and has two volumes for data persistence: `database_data_slave1` and `./database/slave/slave1.cnf` for the MySQL configuration file.

- **slave_db2**: This service represents the second slave database. It has similar characteristics to `slave_db1`, but with a different container name, volume name (`database_data_slave2`), and configuration file (`./database/slave/slave2.cnf`).

- **nginxlb**: This service represents an Nginx load balancer. It is based on the `nginx:1.20.1` image. It exposes port `3310` and depends on the `master_db`, `slave_db1`, `slave_db2`, and `init` services. It is connected to the `network_db` network and has a volume for the Nginx configuration file at `./nginxlb/nginx.conf`.

- **init**: This service is responsible for initializing the database replication setup. It is built using the Dockerfile in the `./init` directory. It depends on the `master_db`, `slave_db1`, and `slave_db2` services to ensure they are running before initialization. It is connected to the `network_db` network and has a volume for the `config.json` file at `./config.json`.

### Possible command Makefile

| Command             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| up                  | This command runs the `docker-compose up` command, which starts the services defined in the Docker Compose file.                                                                                                                                                                                                                                                                                                                                                                                           |
| up-d                | This command runs the `docker-compose up -d` command, which starts the services defined in the Docker Compose file in detached mode, allowing them to run in the background.                                                                                                                                                                                                                                                                                                                            |
| ps                  | This command runs the `docker-compose ps` command, which lists the status of the containers defined in the Docker Compose file.                                                                                                                                                                                                                                                                                                                                                                            |
| down                | This command runs the `docker-compose down --remove-orphans` command, which stops and removes the containers, networks, and volumes defined in the Docker Compose file. The `--remove-orphans` flag ensures that any containers not defined in the Compose file are also removed.                                                                                                                                                                                                                     |
| clean               | This command cleans up the Docker environment by running multiple commands: `docker-compose down --remove-orphans` removes containers, networks, and volumes defined in the Docker Compose file, `docker volume rm` removes specific Docker volumes, and `docker rmi` removes specific Docker images.                                                                                                                                                                                           |
| master-root-cmd     | This command retrieves the host, root user, and root password from the `config.json` file and then executes a MySQL command inside the specified container. It allows executing commands as the root user on the master database.                                                                                                                                                                                                                                                                                  |
| master-wo-cmd       | This command retrieves the host, write-only username, and write-only password from the `config.json` file and then executes a MySQL command inside the specified container. It allows executing commands as the write-only user on the master database.                                                                                                                                                                                                                                                     |
| slave-root-cmd      | This command retrieves the appropriate slave host, root user, and root password from the `config.json` file based on the slave's ID (if available) and then executes a MySQL command inside the specified container. It allows executing commands as the root user on the slave database. If there are multiple slaves, it selects the appropriate host, root user, and root password based on the ID. |
| slave-ro-cmd ID={}  | This command retrieves the appropriate slave host and read-only username and password from the `config.json` file based on the slave's ID (if available) and then executes a MySQL command inside the specified container. It allows executing commands as the read-only user on the slave database. If there are multiple slaves, it selects the appropriate host, read-only username, and password based on the ID.                                                  |
| master-env-generate | This command generates the environment file for the master database by creating a new file or overwriting an existing one. It retrieves the master database's root password from the `config.json` file and writes it along with the `MYSQL_GROUP_REPLICATION=FORCE_PLUS_PERMANENT` configuration to the environment file.                                                                                                                                                                                     |
| slave-env-generate  | This command generates the environment file for the slave database by creating a new file or overwriting an existing one. It retrieves the slave database's root password from the `config.json` file and writes it along with the `MYSQL_GROUP_REPLICATION=FORCE_PLUS_PERMANENT` configuration to the environment file.                                                                                                                                                                                      |


-----------------------------------------------

<h3 align="center">🌟 Thank you for visiting! 🌟</h3>

-----------------------------------------------

📚 Thank you for taking the time to explore this repository. We hope you found the information useful and insightful.

🤝 If you have any questions, feedback, or suggestions, please feel free to reach out. We appreciate hearing from you
and value your input.

⭐️ Remember to star this repository if you found it helpful. It helps us to know that our work is making a difference.

💻 Keep coding, keep learning, and keep pushing the boundaries of what's possible!

-----------------------------------------------
