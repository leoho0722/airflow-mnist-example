.PHONY: run-minio-server
run-minio-server:
	minio server ~/minio --console-address :9001

.PHONY: run-airflow-standalone
run-airflow-standalone:
	export AIRFLOW_HOME=$(pwd) && clear && airflow standalone