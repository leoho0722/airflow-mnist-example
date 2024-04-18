from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client.models import V1ResourceRequirements, V1EnvVar

from config import env

default_args = {
    'owner': 'Leo Ho',
}

with DAG(
    dag_id='mnist-k8s-pipeline',
    default_args=default_args,
    max_active_tasks=1,
    max_active_runs=1
):
    env_vars = [
        V1EnvVar(name="MINIO_API_ENDPOINT", value=env.MINIO_API_ENDPOINT),
        V1EnvVar(name="MINIO_ACCESS_KEY", value=env.MINIO_ACCESS_KEY),
        V1EnvVar(name="MINIO_SECRET_KEY", value=env.MINIO_SECRET_KEY),
        V1EnvVar(name="TRAINING_EPOCHS", value="100")
    ]
    node_selector = {
        "kubernetes.io/hostname": "3070ti"
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

    training = KubernetesPodOperator(
        task_id="mnist-training",
        namespace="default",
        image="leoho0722/airflow-training:0.0.4-k8s-gpu",
        name="mnist-training",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars=env_vars,
        container_resources=V1ResourceRequirements(
            limits={
                "nvidia.com/gpu": 1
            },
        ),
        node_selector=node_selector
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

    buckets_create >> preprocess >> training >> evaluate  # type: ignore
