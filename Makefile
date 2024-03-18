# ===== Install =====

# 一鍵安裝 MinIO Server、MinIO Client、PostgreSQL、pgAdmin4
.PHONY: install
install: install-minio-server install-minio-client install-postgresql

# 安裝 MinIO Server for Linux
.PHONY: install-minio-server
install-minio-server:
	sh ./scripts/install-minio-server.sh

# 安裝 MinIO Client for Linux
.PHONY: install-minio-client
install-minio-client:
	sh ./scripts/install-minio-client.sh

# 安裝 PostgreSQL for Linux 和 pgAdmin4 for Linux
.PHONY: install-postgresql
install-postgresql:
	sh ./scripts/install-postgresql.sh

# ===== Run =====

# 啟動 MinIO Server
.PHONY: run-minio-server
run-minio-server:
	sh ./scripts/run-minio-server.sh

# 設定 MinIO Client 的配置檔
.PHONY: config-minio-client
config-minio-client:
	sh ./scripts/config-minio-client.sh

# 一鍵啟動 Airflow
.PHONY: run-airflow
run-airflow: config-airflow-home-env run-airflow-standalone

# 設定 Airflow Home 環境變數
.PHONY: config-airflow-home-env
config-airflow-home-env:
	export AIRFLOW_HOME=$(pwd)

# 啟動 Airflow Standalone
.PHONY: run-airflow-standalone
run-airflow-standalone:
	clear && airflow standalone