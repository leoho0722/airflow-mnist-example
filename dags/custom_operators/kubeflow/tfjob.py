from airflow.models import BaseOperator
from kubernetes import config
from kubernetes.client.models import (
    V1Container,
    V1ResourceRequirements,
    V1PodTemplateSpec,
    V1PodSpec,
    V1ObjectMeta,
    V1Affinity,
    V1NodeAffinity,
    V1NodeSelector,
    V1NodeSelectorTerm
)
from kubeflow.training.models import (
    KubeflowOrgV1ReplicaSpec,
    KubeflowOrgV1TFJob,
    KubeflowOrgV1TFJobSpec,
    KubeflowOrgV1RunPolicy,
)
from kubeflow.training.api.training_client import TrainingClient


class TFJobKubeflowOperator (BaseOperator):
    """TFJob Kubeflow Operator"""

    def __init__(
        self,
        namespace: str,
        name: str,
        image: str,
        env_vars: list = [],
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

        terms = V1NodeSelectorTerm(
            match_expressions=[
                {
                    'key': 'kubernetes.io/hostname',
                    'operator': 'In',
                    'values': ["ubuntu3070ti"]
                }
            ]
        )
        node_selector = V1NodeSelector(node_selector_terms=terms)
        node_affinity = V1NodeAffinity(
            required_during_scheduling_ignored_during_execution=node_selector
        )
        affinity = V1Affinity()
        affinity.node_affinity = node_affinity
        worker = KubeflowOrgV1ReplicaSpec(
            replicas=self.gpu_num - 1 if self.gpu_num > 1 else 1,
            restart_policy="OnFailure",
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[container],
                    affinity=affinity,
                    node_selector=self.node_selector if self.gpu_num else None
                )
            )
        )
        tf_replica_specs["Worker"] = worker

        # if self.gpu_num > 1:
        #     master = KubeflowOrgV1ReplicaSpec(
        #         replicas=1,
        #         restart_policy="OnFailure",
        #         template=V1PodTemplateSpec(
        #             spec=V1PodSpec(
        #                 containers=[container],
        #                 node_selector=self.node_selector
        #             )
        #         )
        #     )
        #     tf_replica_specs["Master"] = master

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

    # def _create_container(
    #     self,
    #     name: str,
    #     image: str,
    #     env_vars
    # ) -> V1Container:
    #     """建立 Container

    #     Args:
    #         container_name (str): Container 名稱
    #         image (str): Container 映像檔
    #         image_pull_policy (str): 映像檔拉取策略. Defaults to "Always".
    #         env_vars (list[V1EnvVar] | dict[str, str] | None): Container 環境變數. Defaults to {}.
    #         resources (V1ResourceRequirements, optional): Container 資源需求. Defaults to V1ResourceRequirements().
    #     """

    #     container = V1Container(
    #         name=name,
    #         image=image,
    #         image_pull_policy="Always",
    #         env=env_vars,
    #         resources=V1ResourceRequirements(
    #             limits={
    #                 "nvidia.com/gpu": 1
    #             },
    #         )
    #     )
    #     return container

    # def _create_tf_replica_specs(self, container: V1Container):
    #     tf_replica_specs = dict()

    #     worker = KubeflowOrgV1ReplicaSpec(
    #         replicas=self.gpu_num - 1 if self.gpu_num > 1 else 1,
    #         restart_policy="OnFailure",
    #         template=V1PodTemplateSpec(
    #             spec=V1PodSpec(
    #                 containers=[container],
    #                 node_selector=self.node_selector
    #             )
    #         )
    #     )
    #     tf_replica_specs["Worker"] = worker

    #     if self.gpu_num > 1:
    #         master = KubeflowOrgV1ReplicaSpec(
    #             replicas=1,
    #             restart_policy="OnFailure",
    #             template=V1PodTemplateSpec(
    #                 spec=V1PodSpec(
    #                     containers=[container],
    #                     node_selector=self.node_selector
    #                 )
    #             )
    #         )
    #         tf_replica_specs["Master"] = master
    #     return tf_replica_specs

    # def _create_tfjob(self, tf_replica_specs):
    #     """建立 TFJob

    #     Args:
    #         tf_replica_specs (dict[str, KubeflowOrgV1ReplicaSpec])
    #     """

    #     tfjob = KubeflowOrgV1TFJob(
    #         api_version="kubeflow.org/v1",
    #         kind="TFJob",
    #         metadata=V1ObjectMeta(name=self.name),
    #         spec=KubeflowOrgV1TFJobSpec(
    #             run_policy=KubeflowOrgV1RunPolicy(clean_pod_policy=None),
    #             tf_replica_specs=tf_replica_specs
    #         )
    #     )
    #     self.job_client.create_tfjob(tfjob, namespace=self.namespace)

    def execute(self, context):
        self.create_job()
        return "TFJob Executed!"

    def clear(self, context):
        self.job_client.delete_job(self.name, namespace=self.namespace)
