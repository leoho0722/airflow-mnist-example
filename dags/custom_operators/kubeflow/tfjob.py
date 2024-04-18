from typing import Any

from airflow.models import BaseOperator
from airflow.utils.context import Context
from kubernetes import config
from kubernetes.client.models import (
    V1Container,
    V1ResourceRequirements,
    V1PodTemplateSpec,
    V1PodSpec,
    V1ObjectMeta,
)
from kubeflow.training.models import (
    KubeflowOrgV1ReplicaSpec,
    KubeflowOrgV1TFJob,
    KubeflowOrgV1TFJobSpec,
    KubeflowOrgV1RunPolicy,
)
from kubeflow.training.api.training_client import TrainingClient

# Check trained model is uploaded to MinIO Buckets
from config import env
from utils.minio.client import connect_minio
from utils.minio.buckets import object_exists


class KubeTFJobOperator (BaseOperator):
    """Kubeflow TFJob Operator"""

    def __init__(
        self,
        namespace: str,
        name: str,
        image: str,
        env_vars: list = [],
        gpu_num: int = 1,
        node_name=None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        # Load Kube Config
        config.load_kube_config()

        # TFJob
        self.namespace = namespace if namespace else "default"

        # Container
        self.name = name
        self.image = image
        self.env_vars = env_vars

        # GPU
        self.gpu_num = gpu_num
        self.node_name = node_name

        # Training Client
        self.job_client = TrainingClient()

    def execute(self, context: Context) -> Any:
        self.create_job()
        return "TFJob Executed!"

    def create_job(self) -> None:
        # Create Container
        container_resources_limits = {
            "nvidia.com/gpu": 1
        } if self.gpu_num else {
            "cpu": "4000m"
        }
        container = V1Container(
            name="tensorflow",
            image=self.image,
            image_pull_policy="IfNotPresent",
            env=self.env_vars,
            resources=V1ResourceRequirements(limits=container_resources_limits)
        )

        # Create TFReplicaSpecs
        tf_replica_specs = dict()
        worker = KubeflowOrgV1ReplicaSpec(
            replicas=self.gpu_num - 1 if self.gpu_num > 1 else 1,
            restart_policy="OnFailure",
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[container],
                    node_name=self.node_name,
                )
            )
        )
        tf_replica_specs["Worker"] = worker

        if self.gpu_num > 1:
            master = KubeflowOrgV1ReplicaSpec(
                replicas=1,
                restart_policy="OnFailure",
                template=V1PodTemplateSpec(
                    spec=V1PodSpec(
                        containers=[container],
                        node_name=self.node_name,
                    )
                )
            )
            tf_replica_specs["Master"] = master

        # Create TFJob
        tfjob = KubeflowOrgV1TFJob(
            api_version="kubeflow.org/v1",
            kind="TFJob",
            metadata=V1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=KubeflowOrgV1TFJobSpec(
                run_policy=KubeflowOrgV1RunPolicy(clean_pod_policy=None),
                tf_replica_specs=tf_replica_specs
            )
        )
        self.job_client.create_job(tfjob, namespace=self.namespace)

    def clear(self):
        # Check trained model is uploaded to MinIO Buckets or not.
        client = connect_minio()
        while 1:
            isExists = object_exists(
                client=client,
                bucket_name=env.MNIST_TRAINING_MODEL_BUCKET_NAME,
                object_name=env.TRAINED_MODEL_KERAS_FILENAME
            )
            if isExists:
                print(
                    f"{env.TRAINED_MODEL_KERAS_FILENAME} is uploaded to MinIO Buckets..."
                )
                break
            else:
                print(
                    f"{env.TRAINED_MODEL_KERAS_FILENAME} doesn't upload to MinIO Buckets..."
                )

        # Delete TFJob if trained model is uploaded to MinIO Buckets.
        self.job_client.delete_job(self.name, namespace=self.namespace)
