from typing import List, Optional

from kubernetes import client as K8SClient
from pydantic import BaseModel


class ModelService:
    def __init__(self, name: str, namespace: str = "default"):
        self.name = name
        self.namespace = namespace

        self.body: Optional[K8SClient.V1Service] = None

        api = K8SClient.CoreV1Api()
        try:
            self.body = api.read_namespaced_service(name=self.name, namespace=self.namespace)
        except K8SClient.ApiException as err:
            if err.status == 404:
                self.body = None
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
        if self.body:
            return self

        api = K8SClient.CoreV1Api()
        service_body = self.get_service_body()
        self.body = api.create_namespaced_service(
            namespace=self.namespace,
            body=service_body,
        )
        return self

    def delete(self) -> "ModelService":
        if self.body is None or self.body.metadata is None:
            return self

        api = K8SClient.CoreV1Api()
        api.delete_namespaced_service(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
        )
        self.body = None

        return self

    def add_finalizers(self, finalizers: List[str] = None):
        if self.body is None or self.body.metadata is None:
            return self

        api = K8SClient.CoreV1Api()
        if self.body.metadata.finalizers is None:
            self.body.metadata.finalizers = []
        for finalizer in finalizers:
            if finalizer not in self.body.metadata.finalizers:
                self.body.metadata.finalizers.append(finalizer)
        self.body = api.patch_namespaced_service(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
            body=self.body,
        )
        return self

    def remove_finalizers(self, finalizers: List[str] = None):
        if self.body is None or self.body.metadata is None or not self.body.metadata.finalizers:
            return self

        api = K8SClient.CoreV1Api()
        for finalizer in finalizers:
            if finalizer in self.body.metadata.finalizers:
                self.body.metadata.finalizers.remove(finalizer)
        self.body = api.patch_namespaced_service(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
            body=self.body,
        )

        return self
