.EXPORT_ALL_VARIABLES:

ps:
	docker-compose ps

down:
	docker-compose down --remove-orphans

master-it:
	host=$$(echo | awk -F'"' '/"master_database_host"/ { print $$4 }' config.json); \
	r_user=$$(echo | awk -F'"' '/"master_database_root_user"/ { print $$4 }' config.json); \
	r_pasw=$$(echo | awk -F'"' '/"master_database_root_password"/ { print $$4 }' config.json); \
	echo "docker exec -it $${host} mysql -u$${r_user} -p$${r_pasw}"

slave-it:
	host=$$(echo | awk -F'"' '/slave_database_host/ { a[++count] = $$4 } END { if (count >= 2) print a[$(ID)]; else print a[1] }' config.json); \
	r_user=$$(echo | awk -F'"' '/slave_database_root_user/ { a[++count] = $$4 } END { if (count >= 2) print a[$(ID)]; else print a[1] }' config.json); \
	r_pasw=$$(echo | awk -F'"' '/slave_database_root_password/ { a[++count] = $$4 } END { if (count >= 2) print a[$(ID)]; else print a[1] }' config.json); \
	echo "docker exec -it $${host} mysql -u$${r_user} -p$${r_pasw}"