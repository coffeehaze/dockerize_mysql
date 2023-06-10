#!/bin/bash
master_db_host="master_db"
slaves_db_host=("slave1_db" "slave2_db" "slave3_db")

echo "MASTER HOST : $master_db_host"
for index in "${!slaves_db_host[@]}"; do
  echo "SLAVE $((index + 1)) HOST : ${slaves_db_host[$index]}"

  # master_db slave users creation query
  slave_name=${slaves_db_host[$index]}
  query="CREATE USER \"${slave_name}_user\"@\"%\" IDENTIFIED BY \"${slave_name}_pwd\"; GRANT REPLICATION SLAVE ON *.* TO \"${slave_name}_user\"@\"%\"; FLUSH PRIVILEGES;"
  echo $query
done