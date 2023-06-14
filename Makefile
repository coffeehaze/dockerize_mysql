.EXPORT_ALL_VARIABLES:

up:
	docker-compose up

up-d:
	docker-compose up -d

ps:
	docker-compose ps

down:
	docker-compose down --remove-orphans

clean:
	docker-compose down --remove-orphans
	docker volume rm mysql_master_slave_database_data_master -f
	docker volume rm mysql_master_slave_database_data_slave1 -f
	docker volume rm mysql_master_slave_database_data_slave2 -f
	docker rmi mysql_master_slave_master_db -f
	docker rmi mysql_master_slave_slave_db1 -f
	docker rmi mysql_master_slave_slave_db2 -f
	docker rmi mysql_master_slave_init -f

master-root-cmd:
	host=$$(echo | awk -F'"' '/master_database_host/ { print $$4 }' config.json); \
	r_user=$$(echo | awk -F'"' '/master_database_root_user/ { print $$4 }' config.json); \
	r_pasw=$$(echo | awk -F'"' '/master_database_root_password/ { print $$4 }' config.json); \
	docker exec -it $${host} mysql -u$${r_user} -p$${r_pasw}

master-wo-cmd:
	host=$$(echo | awk -F'"' '/master_database_host/ { print $$4 }' config.json); \
	r_user=$$(echo | awk -F'"' '/write_only_username/ { print $$4 }' config.json); \
	r_pasw=$$(echo | awk -F'"' '/write_only_password/ { print $$4 }' config.json); \
	docker exec -it $${host} mysql -u$${r_user} -p$${r_pasw}

slave-root-cmd:
	host=$$(echo | awk -F'"' '/slave_database_host/ { a[++count] = $$4 } END { if (count >= 2) print a[$(ID)]; else print a[1] }' config.json); \
	r_user=$$(echo | awk -F'"' '/slave_database_root_user/ { a[++count] = $$4 } END { if (count >= 2) print a[$(ID)]; else print a[1] }' config.json); \
	r_pasw=$$(echo | awk -F'"' '/slave_database_root_password/ { a[++count] = $$4 } END { if (count >= 2) print a[$(ID)]; else print a[1] }' config.json); \
	docker exec -it $${host} mysql -u$${r_user} -p$${r_pasw}

slave-ro-cmd:
	host=$$(echo | awk -F'"' '/slave_database_host/ { a[++count] = $$4 } END { if (count >= 2) print a[$(ID)]; else print a[1] }' config.json); \
	r_user=$$(echo | awk -F'"' '/read_only_username/ { print $$4 }' config.json); \
	r_pasw=$$(echo | awk -F'"' '/read_only_password/ { print $$4 }' config.json); \
	docker exec -it $${host} mysql -u$${r_user} -p$${r_pasw}

master-env-generate:
	rm -rf ./database/master/.env 
	touch ./database/master/.env
	r_pasw=$$(echo | awk -F'"' '/master_database_root_password/ { print $$4 }' config.json); \
	echo "MYSQL_GROUP_REPLICATION=FORCE_PLUS_PERMANENT" >> ./database/master/.env; \
	echo "MYSQL_ROOT_PASSWORD=$${r_pasw}" >> ./database/master/.env

slave-env-generate:
	rm -rf ./database/slave/.slave$(ID).env
	touch ./database/slave/.slave$(ID).env
	r_pasw=$$(echo | awk -F'"' '/slave_database_root_password/ { a[++count] = $$4 } END { if (count >= 2) print a[$(ID)]; else print a[1] }' config.json); \
	echo "MYSQL_GROUP_REPLICATION=FORCE_PLUS_PERMANENT" >> ./database/slave/.slave$(ID).env; \
	echo "MYSQL_ROOT_PASSWORD=$${r_pasw}" >> ./database/slave/.slave$(ID).env