from typing import Any, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel


class ModelService:
    name: str
    version: Union[str, None]
    namespace: str
    service: Union[Any, None] = None

    def get_service_body(self) -> K8SClient.V1Service:
        service = K8SClient.V1Service(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{self.name}-{self.version}",
                namespace=self.namespace,
            ),
            spec=K8SClient.V1ServiceSpec(
                type="ClusterIP",
                selector={
                    "app": self.name,
                    "version": self.version,
                },
                ports=[
                    K8SClient.V1ServicePort(
                        port=8080,
                        protocol="TCP",
                        target_port=8080,
                    ),
                ],
            ),
        )
        return service

    def create(self) -> "ModelService":
        if self.service is not None:
            return self.update()
        api = K8SClient.CoreV1Api()
        service_body = self.get_service_body()
        self.service = api.create_namespaced_service(
            namespace=self.namespace,
            body=service_body,
        )
        return self

    def update(self) -> "ModelService":
        if self.service is None:
            return self.create()
        api = K8SClient.CoreV1Api()
        service_body = self.get_service_body()
        self.service = api.patch_namespaced_service(
            name=f"{self.name}-{self.version}",
            namespace=self.namespace,
            body=service_body,
        )
        return self

    def delete(self) -> "ModelService":
        api = K8SClient.CoreV1Api()
        api.delete_namespaced_service(
            name=self.service.metadata.name,
            namespace=self.namespace,
        )

        self.service = None

        return self
