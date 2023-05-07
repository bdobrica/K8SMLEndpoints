from typing import Dict, List

from kubernetes import client as K8SClient
from resources.istio import client as IstioClient


class IstioVirtualService:
    def __init__(self, name: str, namespace: str = "default") -> None:
        self.name = name
        self.namespace = namespace
        self.body = IstioClient.V1Beta1Api().read_namespaced_virtual_service(self.name, self.namespace)

    def get_body(
        self, gateway: str, hosts: List[str], destinations: List[Dict[str, str]]
    ) -> IstioClient.V1Beta1VirtualService:
        return IstioClient.V1Beta1VirtualService(
            metadata=IstioClient.V1Beta1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=IstioClient.V1Beta1VirtualServiceSpec(
                gateways=[gateway],
                hosts=hosts,
                http=[
                    IstioClient.V1Beta1Route(
                        route=[
                            IstioClient.V1Beta1Destination(
                                destination=IstioClient.V1Beta1Host(
                                    host=destination.get("host"),
                                    port=IstioClient.V1Beta1Port(number=destination.get("port")),
                                ),
                                weight=destination.get("weight"),
                            )
                        ]
                    )
                    for destination in destinations
                ],
            ),
        )

    def create(self, gateway: str, hosts: List[str], destinations: List[Dict[str, str]]) -> "IstioVirtualService":
        if self.body:
            return self.update(gateway=gateway, hosts=hosts, destinations=destinations)

        api = IstioClient.V1Beta1Api()
        body = self.get_body(gateway=gateway, hosts=hosts, destinations=destinations)
        self.body = api.create_namespaced_virtual_service(namespace=self.namespace, body=body)
        return self

    def update(self, gateway: str, hosts: List[str], destinations: List[Dict[str, str]]) -> "IstioVirtualService":
        if not self.body:
            return self.create(gateway=gateway, hosts=hosts, destinations=destinations)

        api = IstioClient.V1Beta1Api()
        body = self.get_body(gateway=gateway, hosts=hosts, destinations=destinations)
        self.body = api.patch_namespaced_virtual_service(name=self.name, namespace=self.namespace, body=body)
        return self

    def delete(self) -> "IstioVirtualService":
        if self.body is None or self.body.metadata is None:
            return self

        api = IstioClient.V1Beta1Api()
        api.delete_namespaced_virtual_service(name=self.body.metadata.name, namespace=self.body.metadata.namespace)
        self.body = None

        return self

    def add_finalizers(self, finalizers: List[str]) -> "IstioVirtualService":
        if not self.body or not self.body.metadata:
            return self

        api = IstioClient.V1Beta1Api()
        if not self.body.metadata.finalizers:
            self.body.metadata.finalizers = []

        for finalizer in finalizers:
            if finalizer not in self.body.metadata.finalizers:
                self.body.metadata.finalizers.append(finalizer)

        self.body = api.patch_namespaced_virtual_service(
            name=self.body.metadata.name, namespace=self.body.metadata.namespace, body=self.body
        )
        return self

    def remove_finalizers(self, finalizers: List[str]) -> "IstioVirtualService":
        if not self.body or not self.body.metadata or not self.body.metadata.finalizers:
            return self

        api = IstioClient.V1Beta1Api()
        for finalizer in finalizers:
            if finalizer in self.body.metadata.finalizers:
                self.body.metadata.finalizers.remove(finalizer)

        self.body = api.patch_namespaced_virtual_service(
            name=self.body.metadata.name, namespace=self.body.metadata.namespace, body=self.body
        )
        return self
