docker-compose down --remove-orphans
docker volume rm mysql_master_slave_database_data_master mysql_master_slave_database_data_slave1 mysql_master_slave_database_data_slave2 -f
docker rmi mysql_master_slave_slave_db1 mysql_master_slave_slave_db2 mysql_master_slave_master_db mysql_master_slave_init -f