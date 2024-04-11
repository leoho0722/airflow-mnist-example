# ===== Build =====

AUTHOR ?= leoho0722
IMG ?= airflow-k8s-pod-operator-test
IMG_TAG ?= latest
DOCKERFILE_PATH ?= k8s/
TARGET_PLATFORM ?= linux/amd64,linux/arm64
USE_CACHE ?= false

# 一鍵建置多架構 Docker Image，並推送到 Docker Hub
.PHONY: build-image
build-image:
ifeq ($(USE_CACHE), false)
	docker build --push --no-cache -f $(DOCKERFILE_PATH) -t $(AUTHOR)/$(IMG):$(IMG_TAG) . --platform $(TARGET_PLATFORM)
else
	docker build --push -f $(DOCKERFILE_PATH) -t $(AUTHOR)/$(IMG):$(IMG_TAG) . --platform $(TARGET_PLATFORM)
endif

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
run-airflow:
	sh ./scripts/run-airflow.sh