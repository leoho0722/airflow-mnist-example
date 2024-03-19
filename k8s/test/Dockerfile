FROM apache/airflow:slim-2.8.3-python3.10

USER root

# 安裝 pip 套件 (tensorflow、minio)
RUN sudo pip install tensorflow==2.16.1 minio==7.2.5

USER airflow

# 複製 DAG
COPY --chown=airflow:root dags /opt/airflow/dags