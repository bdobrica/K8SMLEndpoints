from typing import Dict, List

import istio_client as IstioClient
from kubernetes import client as K8SClient
from resources.custom_resource import CustomResource


class IstioVirtualService(CustomResource):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(
            name=name, plural="virtualservices", namespace=namespace, group="networking.istio.io", version="v1beta1"
        )

    def create(self, gateway: str, hosts: List[str], destinations: List[Dict[str, str]]) -> "IstioVirtualService":
        if self.data:
            return self.update(gateway=gateway, hosts=hosts, destinations=destinations)

        api = K8SClient.CustomObjectsApi()

        virtual_service_body = IstioClient.V1Beta1VirtualService(
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

        self.data = api.create_namespaced_custom_object(
            group=self.group,
            version=self.version,
            namespace=self.namespace,
            plural=self.plural,
            body=virtual_service_body,
        )

        return self

    def update(self, gateway: str, hosts: List[str], destinations: List[Dict[str, str]]) -> "IstioVirtualService":
        api = K8SClient.CustomObjectsApi()

        virtual_service_body = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
            },
            "spec": {
                "gateways": [
                    gateway,
                ],
                "hosts": hosts,
                "http": [
                    {
                        "route": [
                            {
                                "host": destination.get("host"),
                                "port": {"number": destination.get("port")},
                                "weight": destination.get("weight"),
                            }
                            for destination in destinations
                        ],
                    }
                ],
            },
        }

        self.data = api.patch_namespaced_custom_object(
            group=self.group,
            version=self.version,
            namespace=self.namespace,
            plural=self.plural,
            name=self.name,
            body=virtual_service_body,
        )

        return self

    def delete(self) -> "IstioVirtualService":
        api = K8SClient.CustomObjectsApi()

        api.delete_namespaced_custom_object(
            group=self.group,
            version=self.version,
            namespace=self.namespace,
            plural=self.plural,
            name=self.name,
        )

        self.data = None

        return self
