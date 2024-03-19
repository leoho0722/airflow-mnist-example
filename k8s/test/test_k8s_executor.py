import datetime

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

default_args = {
    'owner': 'Leo Ho',
}

with DAG(
    dag_id="mnist-k8s-pipeline",
    start_date=datetime.datetime(2024, 3, 19),
    default_args=default_args,
):
    podOp = KubernetesPodOperator(
        task_id="mnist-k8s-pipeline",
        namespace="default",
        image="leoho0722/airflow-k8s-pod-operator-test:0.0.1",
        name="mnist-k8s-pipeline",
        labels={"kubernetes.io/hostname": "3070ti"},
    )

    podOp.dry_run()
