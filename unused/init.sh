#!/bin/bash

# Function to execute query and print output
execute_query() {
  local container_name="$1"
  local db_user="$2"
  local db_password="$3"
  local query="$4"

  docker exec "$container_name" sh -c "mysql -u $db_user -p$db_password -e \"$query\""
}

# Variables
master_db="master_db"
master_db_root_pwd="MasterPassword"

# Array of slave details
slaves=(
  "slave_db|SlavePassword|mydb_slave_user|mydb_slave_pwd"
)

# SQL script for creating the replication user on the master
sql_slave_user='CREATE USER "mydb_slave_user"@"%" IDENTIFIED BY "mydb_slave_pwd"; GRANT REPLICATION SLAVE ON *.* TO "mydb_slave_user"@"%"; FLUSH PRIVILEGES;'
execute_query "$master_db" "root" "$master_db_root_pwd" "$sql_slave_user"

# Retrieve the master log file and position
MS_STATUS=$(execute_query "$master_db" "root" "$master_db_root_pwd" "SHOW MASTER STATUS")
CURRENT_LOG=$(echo "$MS_STATUS" | awk '{print $6}')
CURRENT_POS=$(echo "$MS_STATUS" | awk '{print $7}')

# Loop through each slave
for slave in "${slaves[@]}"; do
  IFS='|' read -ra slave_details <<< "$slave"
  slave_db="${slave_details[0]}"
  slave_db_root_pwd="${slave_details[1]}"
  slave_user="${slave_details[2]}"
  slave_password="${slave_details[3]}"

  # SQL script for setting up replication on the slave
  sql_set_master="CHANGE MASTER TO MASTER_HOST='master_db', MASTER_USER='$slave_user', MASTER_PASSWORD='$slave_password', MASTER_LOG_FILE='$CURRENT_LOG', MASTER_LOG_POS=$CURRENT_POS; START SLAVE;"
  execute_query "$slave_db" "root" "$slave_db_root_pwd" "$sql_set_master"

  # Show slave status on the slave
  execute_query "$slave_db" "root" "$slave_db_root_pwd" "SHOW SLAVE STATUS \G"
done
