from typing import List

from resources.mlops import client as MLOpsClient
from resources.model_deployment import ModelDeployment
from resources.model_service import ModelService
from resources.model_storage import ModelStorage
from utils import get_version


class Model:
    def __init__(self, name: str, namespace: str = "default", version: str = ""):
        self.name: str = name
        self.namespace: str = namespace
        self.version: str = version
        self.named_version: str = f"{self.name}-{self.version}" if self.version else self.name

        self.body = MLOpsClient.V1Beta1Api().get_namespaced_model(
            name=self.named_version,
            namespace=namespace,
        )

        self.deployment_name: str = self.named_version
        self.service_name: str = self.named_version
        self.storage_name: str = self.named_version

        self.storage = ModelStorage(name=self.storage_name, namespace=self.namespace)
        self.deployment = ModelDeployment(name=self.deployment_name, namespace=self.namespace)
        self.service = ModelService(name=self.service_name, namespace=self.namespace)

    def get_body(
        self, image: str, artifact: str, command: List[str] = None, args: List[str] = None
    ) -> MLOpsClient.V1Beta1Model:
        return MLOpsClient.V1Beta1Model(
            metadata=MLOpsClient.V1Beta1ObjectMeta(
                name=self.named_version,
                namespace=self.namespace,
                labels={
                    "model": self.name,
                    "version": self.version,
                },
            ),
            spec=MLOpsClient.V1Beta1ModelSpec(
                image=image,
                artifact=artifact,
                command=command,
                args=args,
            ),
        )

    def create(self, image: str, artifact: str, command: List[str] = None, args: List[str] = None) -> "Model":
        if self.body:
            return self

        api = MLOpsClient.V1Beta1Api()
        body = self.get_body(image=image, artifact=artifact, command=command, args=args)
        self.body = api.create_namespaced_model(body=body, namespace=self.namespace)
        return self

    def update(
        self, image: str = None, artifact: str = None, command: List[str] = None, args: List[str] = None
    ) -> "Model":
        if not self.body:
            return self

        api = MLOpsClient.V1Beta1Api()
        body = self.get_body(
            image=image or self.body.spec.image,
            artifact=artifact or self.body.spec.artifact,
            command=command or self.body.spec.command,
            args=args or self.body.spec.args,
        )
        self.body = api.patch_namespaced_model(name=self.name, namespace=self.namespace, body=body)
        return self

    def delete(self) -> "Model":
        if not self.body:
            return self

        api = MLOpsClient.V1Beta1Api()
        api.delete_namespaced_model(name=self.name, namespace=self.namespace)
        self.body = None
        return self

    def create_handler(self, instances: str, cpus: str, memory: str, size: str, path: str) -> "Model":
        self.storage.create(
            size=size,
            path=path,
        )
        self.deployment.create(
            image=self.body.spec.image,
            artifact=self.body.spec.artifact,
            command=self.body.spec.command,
            args=self.body.spec.args,
            instances=instances,
            cpus=cpus,
            memory=memory,
        )
        self.service.create()
        return self

    def update_handler(self, instances: str, cpus: str, memory: str, size: str, path: str) -> "Model":
        return self

    def delete_handler(self):
        self.service.delete()
        self.deployment.delete()
        self.storage.delete()
        return self

    def add_finalizers(self, finalizers: List[str]) -> "Model":
        api = MLOpsClient.V1Beta1Api()
        for finalizer in finalizers:
            if finalizer not in self.body.metadata.finalizers:
                self.body.metadata.finalizers.append(finalizer)
        self.body = api.update_namespaced_model(name=self.name, namespace=self.namespace, body=self.body)
        return self

    def remove_finalizers(self, finalizers: List[str]) -> "Model":
        api = MLOpsClient.V1Beta1Api()
        for finalizer in finalizers:
            if finalizer in self.body.metadata.finalizers:
                self.body.metadata.finalizers.remove(finalizer)
        self.body = api.update_namespaced_model(name=self.name, namespace=self.namespace, body=self.body)
        return self
