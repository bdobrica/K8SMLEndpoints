from typing import Any, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel
from resources.model_storage import ModelStorage


class ModelDeployment(BaseModel):
    name: str
    namespace: str
    version: Union[str, None]
    image: str
    init_image: str = "quay.io/bdobrica/ml-operator-tools:model-init-latest"
    artifact: str
    instances: int
    cpus: str
    memory: str
    deployment: Union[Any, None] = None

    def get_deployment_body(self) -> K8SClient.V1Deployment:
        deployment_body = K8SClient.V1Deployment(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{self.name}-{self.version}",
                namespace=self.namespace,
            ),
            spec=K8SClient.V1DeploymentSpec(
                replicas=self.instances,
                selector=K8SClient.V1LabelSelector(
                    match_labels={
                        "app": self.name,
                        "version": self.version,
                    }
                ),
                strategy=K8SClient.V1DeploymentStrategy(
                    type="RollingUpdate",
                ),
                template=K8SClient.V1PodTemplateSpec(
                    metadata=K8SClient.V1ObjectMeta(
                        labels={
                            "app": self.name,
                            "version": self.version,
                        }
                    ),
                    spec=K8SClient.V1PodSpec(
                        init_containers=[
                            K8SClient.V1Container(
                                image=self.INIT_IMAGE,
                                name=f"{self.name}-init",
                                env=[
                                    K8SClient.V1EnvVar(
                                        name="MODEL_URL",
                                        value=self.artifact,
                                    ),
                                    K8SClient.V1EnvVar(
                                        name="MODEL_PATH",
                                        value="/opt/ml",
                                    ),
                                ],
                                volume_mounts=[
                                    K8SClient.V1VolumeMount(
                                        name=f"{self.name}-{self.version}",
                                        mount_path="/opt/ml",
                                        read_only=True,
                                    )
                                ],
                            )
                        ],
                        containers=[
                            K8SClient.V1Container(
                                name=self.name,
                                image=self.image,
                                resources=K8SClient.V1ResourceRequirements(
                                    limits={
                                        "cpu": self.cpus,
                                        "memory": self.memory,
                                    },
                                    requests={
                                        "cpu": self.cpus,
                                        "memory": self.memory,
                                    },
                                ),
                                volume_mounts=[
                                    K8SClient.V1VolumeMount(
                                        name=f"{self.name}-{self.version}",
                                        mount_path="/opt/ml",
                                    ),
                                ],
                            ),
                        ],
                        volumes=[
                            K8SClient.V1Volume(
                                name=f"{self.name}-{self.version}",
                                persistent_volume_claim=K8SClient.V1PersistentVolumeClaimVolumeSource(
                                    claim_name=f"{self.name}-pvc",
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        )
        return deployment_body

    def create(self) -> "ModelDeployment":
        if self.deployment is not None:
            return self.update()

        api = K8SClient.AppsV1Api()
        deployment_body = self.get_deployment_body()
        self.deployment = api.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_body,
        )
        return self

    def update(self) -> "ModelDeployment":
        if self.deployment is None:
            return self.create()

        api = K8SClient.AppsV1Api()
        deployment_body = self.get_deployment_body()
        self.deployment = api.patch_namespaced_deployment(
            name=f"{self.name}-{self.version}",
            namespace=self.namespace,
            body=deployment_body,
        )
        return self

    def delete(self) -> "ModelDeployment":
        api = K8SClient.AppsV1Api()
        api.delete_namespaced_deployment(
            name=f"{self.name}-{self.version}",
            namespace=self.namespace,
        )

        self.deployment = None
        return self
