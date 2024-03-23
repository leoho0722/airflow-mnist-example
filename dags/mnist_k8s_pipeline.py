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
    buckets_create_op = KubernetesPodOperator(
        task_id="mnist-buckets-create",
        namespace="default",
        image="leoho0722/airflow-buckets-create:0.0.3-k8s",
        name="mnist-buckets-create",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars={
            "MINIO_API_ENDPOINT": "10.20.1.229:9000",
            "MINIO_ACCESS_KEY": "minioadmin",
            "MINIO_SECRET_KEY": "minioadmin",
        },
        # node_selector={
        #     "kubernetes.io/hostname": "ubuntu"
        # }
    )

    preprocess_op = KubernetesPodOperator(
        task_id="mnist-preprocess",
        namespace="default",
        image="leoho0722/airflow-preprocess:0.0.3-k8s",
        name="mnist-preprocess",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars={
            "MINIO_API_ENDPOINT": "10.20.1.229:9000",
            "MINIO_ACCESS_KEY": "minioadmin",
            "MINIO_SECRET_KEY": "minioadmin",
        },
        # node_selector={
        #     "kubernetes.io/hostname": "ubuntu"
        # }
    )

    training_op = KubernetesPodOperator(
        task_id="mnist-training",
        namespace="default",
        image="leoho0722/airflow-training:0.0.3-k8s",
        name="mnist-training",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars={
            "MINIO_API_ENDPOINT": "10.20.1.229:9000",
            "MINIO_ACCESS_KEY": "minioadmin",
            "MINIO_SECRET_KEY": "minioadmin",
        },
        # node_selector={
        #     "kubernetes.io/hostname": "ubuntu"
        # }
    )

    evaluate_op = KubernetesPodOperator(
        task_id="mnist-evaluate",
        namespace="default",
        image="leoho0722/airflow-evaluate:0.0.3-k8s",
        name="mnist-evaluate",
        startup_timeout_seconds=1200,
        image_pull_policy="Always",
        env_vars={
            "MINIO_API_ENDPOINT": "10.20.1.229:9000",
            "MINIO_ACCESS_KEY": "minioadmin",
            "MINIO_SECRET_KEY": "minioadmin",
        },
        # node_selector={
        #     "kubernetes.io/hostname": "ubuntu"
        # }
    )

    buckets_create_op >> preprocess_op >> training_op >> evaluate_op
