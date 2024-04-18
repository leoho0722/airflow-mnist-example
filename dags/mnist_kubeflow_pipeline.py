from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client.models import V1EnvVar

from config import env
from custom_operators.kubeflow.tfjob import KubeTFJobOperator

default_args = {
    'owner': 'Leo Ho',
}

with DAG(
    dag_id='mnist-kubeflow-pipeline',
    default_args=default_args,
    max_active_tasks=1,
    max_active_runs=1
):
    env_vars = [
        V1EnvVar(name="MINIO_API_ENDPOINT", value=env.MINIO_API_ENDPOINT),
        V1EnvVar(name="MINIO_ACCESS_KEY", value=env.MINIO_ACCESS_KEY),
        V1EnvVar(name="MINIO_SECRET_KEY", value=env.MINIO_SECRET_KEY),
        V1EnvVar(name="TRAINING_EPOCHS", value="10")
    ]
    node_selector = {
        "kubernetes.io/hostname": "ubuntu3070ti"
    }

    buckets_create = KubernetesPodOperator(
        task_id="mnist-buckets-create",
        namespace="default",
        image="leoho0722/airflow-buckets-create:0.0.3-k8s",
        name="mnist-buckets-create",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars=env_vars,
    )

    preprocess = KubernetesPodOperator(
        task_id="mnist-preprocess",
        namespace="default",
        image="leoho0722/airflow-preprocess:0.0.3-k8s",
        name="mnist-preprocess",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars=env_vars,
    )

    training_tfjob = KubeTFJobOperator(
        task_id="tensorflow",
        namespace="kubeflow",
        name="tensorflow",
        image="leoho0722/airflow-training:0.0.4-k8s-gpu",
        env_vars=env_vars,
        node_name="ubuntu3070ti"
    )

    terminating_tfjob = PythonOperator(
        task_id="terminating-tfjob",
        python_callable=training_tfjob.clear
    )

    evaluate = KubernetesPodOperator(
        task_id="mnist-evaluate",
        namespace="default",
        image="leoho0722/airflow-evaluate:0.0.4-k8s",
        name="mnist-evaluate",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars=env_vars,
    )

    buckets_create >> preprocess >> training_tfjob >> terminating_tfjob >> evaluate
