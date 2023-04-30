from typing import Any, List, Optional

from kubernetes import client as K8SClient
from pydantic import BaseModel
from resources.model_storage import ModelStorage


class ModelDeployment(BaseModel):
    def __init__(self, name: str, namespace: str):
        self.name = name
        self.namespace = namespace

        self.pvc_name = f"{self.name}-pvc"
        self.body: Optional[K8SClient.V1Deployment] = None

        api = K8SClient.AppsV1Api()
        try:
            self.body = api.read_namespaced_deployment(name=self.name, namespace=self.namespace)
        except K8SClient.ApiException as err:
            if err.status == 404:
                self.body = None
            else:
                raise

    def get_deployment_body(
        self,
        instances: int,
        artifact: str,
        image: str,
        cpus: str,
        memory: str,
        command: List[str] = None,
        args: List[str] = None,
        init_image: str = "quay.io/bdobrica/ml-operator-tools:model-init-latest",
        finalizers: List[str] = None,
    ) -> K8SClient.V1Deployment:
        deployment_body = K8SClient.V1Deployment(
            metadata=K8SClient.V1ObjectMeta(
                name=self.name,
                namespace=self.namespace,
                finalizers=finalizers,
            ),
            spec=K8SClient.V1DeploymentSpec(
                replicas=instances,
                selector=K8SClient.V1LabelSelector(
                    match_labels={
                        "model": self.name,
                    }
                ),
                strategy=K8SClient.V1DeploymentStrategy(
                    type="RollingUpdate",
                ),
                template=K8SClient.V1PodTemplateSpec(
                    metadata=K8SClient.V1ObjectMeta(
                        labels={
                            "model": self.name,
                        }
                    ),
                    spec=K8SClient.V1PodSpec(
                        init_containers=[
                            K8SClient.V1Container(
                                image=init_image,
                                name=f"{self.name}-init",
                                env=[
                                    K8SClient.V1EnvVar(
                                        name="MODEL_URL",
                                        value=artifact,
                                    ),
                                    K8SClient.V1EnvVar(
                                        name="MODEL_PATH",
                                        value="/opt/ml",
                                    ),
                                ],
                                volume_mounts=[
                                    K8SClient.V1VolumeMount(
                                        name=self.name,
                                        mount_path="/opt/ml",
                                        read_only=True,
                                    )
                                ],
                            )
                        ],
                        containers=[
                            K8SClient.V1Container(
                                name=self.name,
                                image=image,
                                command=command,
                                args=args,
                                resources=K8SClient.V1ResourceRequirements(
                                    limits={
                                        "cpu": cpus,
                                        "memory": memory,
                                    },
                                    requests={
                                        "cpu": cpus,
                                        "memory": memory,
                                    },
                                ),
                                volume_mounts=[
                                    K8SClient.V1VolumeMount(
                                        name=self.name,
                                        mount_path="/opt/ml",
                                    ),
                                ],
                            ),
                        ],
                        volumes=[
                            K8SClient.V1Volume(
                                name=self.name,
                                persistent_volume_claim=K8SClient.V1PersistentVolumeClaimVolumeSource(
                                    claim_name=self.pvc_name,
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        )
        return deployment_body

    def create(
        self,
        instances: int,
        artifact: str,
        image: str,
        cpus: str,
        memory: str,
        command: List[str] = None,
        args: List[str] = None,
        init_image: str = "quay.io/bdobrica/ml-operator-tools:model-init-latest",
    ) -> "ModelDeployment":
        if self.body is not None:
            return self.update()

        api = K8SClient.AppsV1Api()
        deployment_body = self.get_deployment_body(
            instances=instances,
            artifact=artifact,
            image=image,
            cpus=cpus,
            memory=memory,
            command=command,
            args=args,
            init_image=init_image,
        )
        self.body = api.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment_body,
        )
        return self

    def update(
        self,
        instances: int,
        artifact: str,
        image: str,
        cpus: str,
        memory: str,
        command: List[str] = None,
        args: List[str] = None,
        init_image: str = "quay.io/bdobrica/ml-operator-tools:model-init-latest",
        finalizers: List[str] = None,
    ) -> "ModelDeployment":
        if self.body is None:
            return self.create()

        api = K8SClient.AppsV1Api()
        deployment_body = self.get_deployment_body(
            instances=instances,
            artifact=artifact,
            image=image,
            cpus=cpus,
            memory=memory,
            command=command,
            args=args,
            init_image=init_image,
            finalizers=finalizers,
        )
        self.body = api.patch_namespaced_deployment(
            name=self.name,
            namespace=self.namespace,
            body=deployment_body,
        )
        return self

    def delete(self) -> "ModelDeployment":
        if self.body is None or self.body.metadata is None:
            return self

        api = K8SClient.AppsV1Api()
        api.delete_namespaced_deployment(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
        )

        self.body = None
        return self

    def add_finalizers(self, finalizers: List[str]) -> "ModelDeployment":
        if self.body is None or not self.body.metadata:
            return self

        api = K8SClient.AppsV1Api()
        if not self.body.metadata.finalizers:
            self.body.metadata.finalizers = []

        for finalizer in finalizers:
            if finalizer not in self.body.metadata.finalizers:
                self.body.metadata.finalizers.append(finalizer)
        self.body = api.patch_namespaced_deployment(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
            body=self.body,
        )

        return self

    def remove_finalizers(self, finalizers: List[str]) -> "ModelDeployment":
        if self.body is None or not self.body.metadata or not self.body.metadata.finalizers:
            return self

        api = K8SClient.AppsV1Api()

        for finalizer in finalizers:
            if finalizer in self.body.metadata.finalizers:
                self.body.metadata.finalizers.remove(finalizer)
        self.body = api.patch_namespaced_deployment(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
            body=self.body,
        )

        return self
