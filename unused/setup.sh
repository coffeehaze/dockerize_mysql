#!/bin/bash
sql_slave_user='CREATE USER "mydb_slave_user"@"%" IDENTIFIED BY "mydb_slave_pwd"; GRANT REPLICATION SLAVE ON *.* TO "mydb_slave_user"@"%"; FLUSH PRIVILEGES;'
docker exec master_db sh -c "mysql -u root -pMasterPassword -e '$sql_slave_user'"
MS_STATUS=`docker exec master_db sh -c 'mysql -u root -pMasterPassword -e "SHOW MASTER STATUS"'`
CURRENT_LOG=`echo $MS_STATUS | awk '{print $6}'`
CURRENT_POS=`echo $MS_STATUS | awk '{print $7}'`
sql_set_master="CHANGE MASTER TO MASTER_HOST='master_db',MASTER_USER='mydb_slave_user',MASTER_PASSWORD='mydb_slave_pwd',MASTER_LOG_FILE='$CURRENT_LOG',MASTER_LOG_POS=$CURRENT_POS; START SLAVE;"
start_slave_cmd='mysql -u root -pSlavePassword -e "'
start_slave_cmd+="$sql_set_master"
start_slave_cmd+='"'
docker exec slave_db sh -c "$start_slave_cmd"
docker exec slave_db sh -c "mysql -u root -pSlavePassword -e 'SHOW SLAVE STATUS \G'"