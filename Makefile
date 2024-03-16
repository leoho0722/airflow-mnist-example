# ===== Install =====

# 一鍵安裝 MinIO Server 和 MinIO Client
.PHONY: install
install: install-minio-server install-minio-client

# 安裝 MinIO Server for Linux
.PHONY: install-minio-server
install-minio-server:
	sh ./scripts/install-minio-server.sh

# 安裝 MinIO Client for Linux
.PHONY: install-minio-client
install-minio-client:
	sh ./scripts/install-minio-client.sh

# ===== Run =====

# 設定 MinIO Client 的配置檔
.PHONY: config-minio-client
config-minio-client:
	sh ./scripts/config-minio-client.sh

# 啟動 MinIO Server
.PHONY: run-minio-server
run-minio-server:
	sh ./scripts/run-minio-server.sh

# 啟動 Airflow Standalone
.PHONY: run-airflow-standalone
run-airflow-standalone:
	export AIRFLOW_HOME=$(pwd) && clear && airflow standalone