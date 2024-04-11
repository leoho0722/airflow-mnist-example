from airflow.models import BaseOperator
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
        env_vars: list[V1EnvVar] = [],
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
        self.job_client.delete_job(self.name, namespace=self.namespace)

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
        self.job_client.create_job(tfjob, namespace=self.namespace)
