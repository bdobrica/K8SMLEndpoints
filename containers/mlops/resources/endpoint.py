from typing import Any

from kubernetes import client as K8SClient
from resources.custom_resource import CustomResource
from resources.endpoint_config import EndpointConfig


class Endpoint(CustomResource):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name, "machinelearningendpoints", namespace)
        self.config = EndpointConfig(self.data.get("spec", {}).get("config"), self.namespace).set_metadata(
            {"endpoint": self.name}
        )

        self.gateway: Any = None
        self.endpoint_config: EndpointConfig = None

    def create(self) -> "Endpoint":
        api = K8SClient.CustomObjectsApi()

        gateway_body = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "Gateway",
            "metadata": {
                "name": f"{self.name}-gw",
                "namespace": self.namespace,
            },
            "spec": {
                "selector": {
                    "istio": "ingressgateway",
                },
                "servers": [
                    {
                        "hosts": [self.data.get("spec", {}).get("host")],
                        "port": {
                            "name": "http",
                            "number": 8080,
                            "protocol": "HTTP",
                        },
                    },
                ],
            },
        }
        self.gateway = api.create_namespaced_custom_object(
            group="networking.istio.io",
            version="v1beta1",
            namespace=self.namespace,
            plural="gateways",
            body=gateway_body,
        )

        self.endpoint_config = EndpointConfig().create(
            endpoint=self.name,
            hosts=[self.data.get("spec", {}).get("host")],
        )
