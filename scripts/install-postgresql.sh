#!/bin/bash

# ===== Install PostgreSQL =====
# Official: https://www.postgresql.org/download/linux/ubuntu/
# Reference: https://www.cherryservers.com/blog/how-to-install-and-setup-postgresql-server-on-ubuntu-20-04

# 切回根目錄
cd ~

# Create the file repository configuration:
sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

# Import the repository signing key:
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Update the package lists:
sudo apt-get update

# Install the latest version of PostgreSQL.
# If you want a specific version, use 'postgresql-16' or similar instead of 'postgresql':
sudo apt-get -y install postgresql

# ===== 檢查 PostgreSQL 服務狀態 =====
service postgresql status

# ===== 建立 PostgreSQL 使用者 =====
# sudo -u postgres psql
# postgres=# \conninfo # 查看連線資訊
# postgres=# \password postgres # 修改 postgres 使用者密碼
# postgres=# CREATE DATABASE airflow_db; # 建立資料庫
# postgres=# \l # 列出所有資料庫

# ===== Install pgAdmin4 =====
# Official: https://www.pgadmin.org/download/pgadmin-4-apt/

# Install the public key for the repository (if not done previously):
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

# Create the repository configuration file:
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'

# Install for both desktop and web modes:
sudo apt install -y pgadmin4

# Configure the webserver, if you installed pgadmin4-web:
sudo /usr/pgadmin4/bin/setup-web.sh

# ===== 啟動 pgAdmin4 =====
# Email: admin@admin.com
# Password: postgres
# 開啟瀏覽器，輸入 http://localhost/pgadmin4
# 點選 Add New Server，填入以下資訊
# General/Name: Airflow
# Connection/Host name/address: localhost
# Connection/Port: 5432
# Connection/Maintenance database: airflow_db
# Connection/Username: postgres
# Connection/Password: postgres

# ===== 修改 airflo.cfg =====
# 先啟動 airflow standalone，產生 airflow.cfg
# 再停止 airflow，修改 airflow.cfg
# sql_alchemy_conn = postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_db
# executor = LocalExecutor