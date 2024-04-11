from datetime import datetime

from airflow import DAG
from airflow.models import BaseOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes import config
from kubernetes.client.models import V1Container, V1ResourceRequirements, V1PodTemplateSpec, V1PodSpec, V1ObjectMeta, V1EnvVar
from kubeflow.training import KubeflowOrgV1ReplicaSpec, KubeflowOrgV1TFJob, KubeflowOrgV1TFJobSpec, KubeflowOrgV1RunPolicy, TrainingClient


class TFJobKubeflowOperator (BaseOperator):
    """TFJob Kubeflow Operator"""

    def __init__(
        self,
        namespace: str,
        name: str,
        image: str,
        env_vars=None,
        gpu_num: int = 1,
        node_selector=None,
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
        self.node_selector = node_selector

        # Training Client
        self.job_client = TrainingClient()

    def execute(self, context):
        self.create_job()
        return "TFJob Executed!"

    def clear(self, context):
        self.job_client.delete_tfjob(self.name, namespace=self.namespace)

    def create_job(self) -> None:
        container = self._create_container(
            name=self.name,
            image=self.image,
            env_vars=self.env_vars
        )
        tf_replica_specs = self._create_tf_replica_specs(container)
        self._create_tfjob(tf_replica_specs)

    def _create_container(
        self,
        name: str,
        image: str,
        env_vars
    ) -> V1Container:
        """建立 Container

        Args:
            container_name (str): Container 名稱
            image (str): Container 映像檔
            image_pull_policy (str): 映像檔拉取策略. Defaults to "Always".
            env_vars (list[V1EnvVar] | dict[str, str] | None): Container 環境變數. Defaults to {}.
            resources (V1ResourceRequirements, optional): Container 資源需求. Defaults to V1ResourceRequirements().
        """

        container = V1Container(
            name=name,
            image=image,
            image_pull_policy="Always",
            env=env_vars,
            resources=V1ResourceRequirements(
                limits={
                    "nvidia.com/gpu": 1
                },
                requests={
                    "nvidia.com/gpu": 1
                },
            )
        )
        return container

    def _create_tf_replica_specs(self, container: V1Container):
        tf_replica_specs = dict()

        worker = KubeflowOrgV1ReplicaSpec(
            replicas=self.gpu_num - 1 if self.gpu_num > 1 else 1,
            restart_policy="OnFailure",
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[container],
                    node_selector=self.node_selector
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
                        node_selector=self.node_selector
                    )
                )
            )
            tf_replica_specs["Master"] = master
        return tf_replica_specs

    def _create_tfjob(self, tf_replica_specs):
        """建立 TFJob

        Args:
            tf_replica_specs (dict[str, KubeflowOrgV1ReplicaSpec])
        """

        tfjob = KubeflowOrgV1TFJob(
            api_version="kubeflow.org/v1",
            kind="TFJob",
            metadata=V1ObjectMeta(name=self.name),
            spec=KubeflowOrgV1TFJobSpec(
                run_policy=KubeflowOrgV1RunPolicy(clean_pod_policy=None),
                tf_replica_specs=tf_replica_specs
            )
        )
        self.job_client.create_tfjob(tfjob, namespace=self.namespace)


default_args = {
    'owner': 'Leo Ho',
}

with DAG(
    dag_id='mnist-k8s-kubeflow-pipeline',
    default_args=default_args,
    start_date=datetime(2024, 3, 20),
    max_active_tasks=1,
    max_active_runs=1
):
    env_vars = [
        V1EnvVar(name="MINIO_API_ENDPOINT", value="10.0.0.196:9000"),
        V1EnvVar(name="MINIO_ACCESS_KEY", value="minioadmin"),
        V1EnvVar(name="MINIO_SECRET_KEY", value="minioadmin"),
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

    training_tfjob = TFJobKubeflowOperator(
        task_id="mnist-training-tfjob",
        namespace="default",
        name="mnist-training-tfjob",
        image="leoho0722/airflow-training:0.0.4-k8s-gpu",
        env_vars=env_vars,
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

    buckets_create >> preprocess >> training_tfjob >> evaluate
