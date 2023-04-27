from typing import Any, List, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel


class ModelService:
    def __init__(self, name: str, namespace: str = "default"):
        self.name = name
        self.namespace = namespace

        api = K8SClient.CoreV1Api()
        try:
            self.service = api.read_namespaced_service(f"{self.name}-{self.version}", self.namespace)
        except K8SClient.ApiException as err:
            if err.status == 404:
                self.service = None
            else:
                raise

    def get_service_body(self, finalizers: List[str] = None) -> K8SClient.V1Service:
        service = K8SClient.V1Service(
            metadata=K8SClient.V1ObjectMeta(
                name=self.name,
                namespace=self.namespace,
                finalizers=finalizers,
            ),
            spec=K8SClient.V1ServiceSpec(
                type="ClusterIP",
                selector={
                    "model": self.name,
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
            return self

        api = K8SClient.CoreV1Api()
        service_body = self.get_service_body()
        self.service = api.create_namespaced_service(
            namespace=self.namespace,
            body=service_body,
        )
        return self

    def delete(self) -> "ModelService":
        if self.service is None:
            return self

        api = K8SClient.CoreV1Api()
        api.delete_namespaced_service(
            name=self.name,
            namespace=self.namespace,
        )
        self.service = None

        return self

    def add_finalizers(self, finalizers: List[str] = None):
        if self.service is None:
            return self
        return self

    def remove_finalizers(self, finalizers: List[str] = None):
        if self.service is None:
            return self
        return self
