from datetime import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client.models.v1_resource_requirements import V1ResourceRequirements

default_args = {
    'owner': 'Leo Ho',
}

with DAG(
    dag_id='mnist-k8s-pipeline',
    default_args=default_args,
    start_date=datetime(2024, 3, 20),
):
    env_vars = {
        "MINIO_API_ENDPOINT": "10.0.0.196:9000",
        "MINIO_ACCESS_KEY": "minioadmin",
        "MINIO_SECRET_KEY": "minioadmin",
        "TRAINING_EPOCHS": "10"
    }
    node_selector = {
        "kubernetes.io/hostname": "3070ti"
    }

    buckets_create_op = KubernetesPodOperator(
        task_id="mnist-buckets-create",
        namespace="default",
        image="leoho0722/airflow-buckets-create:0.0.3-k8s",
        name="mnist-buckets-create",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars=env_vars,
        node_selector=node_selector
    )

    preprocess_op = KubernetesPodOperator(
        task_id="mnist-preprocess",
        namespace="default",
        image="leoho0722/airflow-preprocess:0.0.3-k8s",
        name="mnist-preprocess",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars=env_vars,
        node_selector=node_selector
    )

    training_op = KubernetesPodOperator(
        task_id="mnist-training",
        namespace="default",
        image="leoho0722/airflow-training:0.0.3-k8s-gpu",
        name="mnist-training",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars=env_vars,
        container_resources=V1ResourceRequirements(
            limits={
                "nvidia.com/gpu": 1
            },
            requests={
                "nvidia.com/gpu": 1
            },
        ),
        node_selector=node_selector
    )

    evaluate_op = KubernetesPodOperator(
        task_id="mnist-evaluate",
        namespace="default",
        image="leoho0722/airflow-evaluate:0.0.3-k8s",
        name="mnist-evaluate",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars=env_vars,
        node_selector=node_selector
    )

    buckets_create_op >> preprocess_op >> training_op >> evaluate_op
