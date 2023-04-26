from typing import Dict, List

from kubernetes import client as K8SClient
from resources.istio import client as IstioClient


class IstioVirtualService:
    def __init__(self, name: str, namespace: str = "default") -> None:
        self.name = name
        self.namespace = namespace
        self.body = IstioClient.V1Beta1Api().get_namespaced_virtual_service(self.name, self.namespace)

    def get_body(
        self, gateway: str, hosts: List[str], destinations: List[Dict[str, str]]
    ) -> IstioClient.V1Beta1VirtualService:
        return IstioClient.V1Beta1VirtualService(
            metadata=IstioClient.V1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=IstioClient.V1Beta1VirtualServiceSpec(
                gateways=[gateway],
                hosts=hosts,
                http=[
                    IstioClient.V1Beta1Destination(
                        route=[
                            IstioClient.V1Beta1Route(
                                host=destination.get("host"),
                                port=IstioClient.V1Beta1Port(number=destination.get("port")),
                                weight=destination.get("weight"),
                            )
                            for destination in destinations
                        ]
                    )
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

        api = K8SClient.CustomObjectsApi()
        body = self.get_body(gateway=gateway, hosts=hosts, destinations=destinations)
        self.body = api.patch_namespaced_custom_object(name=self.name, namespace=self.namespace, body=body)
        return self

    def delete(self) -> "IstioVirtualService":
        if not self.body:
            return self

        api = IstioClient.V1Beta1Api()
        api.delete_namespaced_virtual_service(name=self.name, namespace=self.namespace)
        self.body = None

        return self
