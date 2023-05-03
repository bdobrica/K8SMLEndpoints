from typing import Dict, List

from kubernetes import client as K8SClient
from resources.istio import client as IstioClient


class IstioGateway:
    def __init__(self, name: str, namespace: str = "default") -> None:
        self.name = name
        self.namespace = namespace
        self.body = IstioClient.V1Beta1Api().read_namespaced_gateway(self.name, self.namespace)

    def get_body(self, labels: Dict[str, str], hosts: List[str], port: int) -> IstioClient.V1Beta1Gateway:
        return IstioClient.V1Beta1Gateway(
            metadata=IstioClient.V1Beta1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=IstioClient.V1Beta1GatewaySpec(
                selector=labels,
                servers=[
                    IstioClient.V1Beta1Server(
                        hosts=hosts,
                        port=IstioClient.V1Beta1Port(
                            name="http",
                            number=port,
                            protocol="HTTP",
                        ),
                    )
                ],
            ),
        )

    def create(self, labels: Dict[str, str], hosts: List[str], port: int) -> "IstioGateway":
        if self.body:
            return self.update(hosts=hosts, port=port)

        api = IstioClient.V1Beta1Api()
        body = self.get_body(labels=labels, hosts=hosts, port=port)
        self.body = api.create_namespaced_gateway(namespace=self.namespace, body=body)

        return self

    def update(self, labels: Dict[str, str], hosts: List[str], port: int) -> "IstioGateway":
        if not self.body:
            return self.create(hosts=hosts, port=port)

        api = IstioClient.V1Beta1Api()
        body = self.get_body(labels=labels, hosts=hosts, port=port)
        self.body = api.patch_namespaced_gateway(name=self.name, namespace=self.namespace, body=body)
        return self

    def delete(self) -> "IstioGateway":
        if not self.body:
            return self

        api = IstioClient.V1Beta1Api()
        api.delete_namespaced_gateway(name=self.name, namespace=self.namespace)
        self.body = None

        return self

    def add_finalizers(self, finalizers: List[str]) -> "IstioGateway":
        if not self.body or not self.body.metadata:
            return self

        api = IstioClient.V1Beta1Api()
        if not self.body.metadata.finalizers:
            self.body.metadata.finalizers = []

        for finalizer in finalizers:
            if finalizer not in self.body.metadata.finalizers:
                self.body.metadata.finalizers.append(finalizer)

        self.body = api.patch_namespaced_gateway(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
            body=self.body,
        )

        return self

    def remove_finalizers(self, finalizers: List[str]) -> "IstioGateway":
        if not self.body or not self.body.metadata or not self.body.metadata.finalizers:
            return self

        api = IstioClient.V1Beta1Api()
        for finalizer in finalizers:
            if finalizer in self.body.metadata.finalizers:
                self.body.metadata.finalizers.remove(finalizer)

        self.body = api.patch_namespaced_gateway(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
            body=self.body,
        )

        return self
