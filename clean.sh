docker-compose down --remove-orphans
docker volume rm mysql_master_slave_database_data_master -f
docker volume rm mysql_master_slave_database_data_slave1 -f
docker volume rm mysql_master_slave_database_data_slave2 -f
docker rmi mysql_master_slave_master_db -f
docker rmi mysql_master_slave_slave_db1 -f
docker rmi mysql_master_slave_slave_db2 -f
docker rmi mysql_master_slave_init -f