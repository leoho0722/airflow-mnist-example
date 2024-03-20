from datetime import datetime

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

default_args = {
    'owner': 'Leo Ho',
}

with DAG(
    dag_id='mnist-k8s-pipeline',
    default_args=default_args,
    start_date=datetime(2024, 3, 20),
):
    preprocessOp = KubernetesPodOperator(
        task_id="mnist-preprocess",
        namespace="default",
        image="leoho0722/airflow-preprocess:0.0.1",
        name="mnist-preprocess",
        node_selector={
            "kubernetes.io/hostname": "ubuntu"
        }
    )

    trainingOp = KubernetesPodOperator(
        task_id="mnist-training",
        namespace="default",
        image="leoho0722/airflow-training:0.0.1",
        name="mnist-training",
        node_selector={
            "kubernetes.io/hostname": "ubuntu"
        }
    )

    evalueateOp = KubernetesPodOperator(
        task_id="mnist-evaluate",
        namespace="default",
        image="leoho0722/airflow-evaluate:0.0.1",
        name="mnist-evaluate",
        node_selector={
            "kubernetes.io/hostname": "ubuntu"
        }
    )

    preprocessOp >> trainingOp >> evalueateOp
