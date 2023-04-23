from typing import Any

from kubernetes import client as K8SClient
from resources.custom_resource import CustomResource
from resources.endpoint_config import EndpointConfig
from resources.istio_gateway import IstioGateway


class Endpoint(CustomResource):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name, "machinelearningendpoints", namespace)

        self.gateway_name = f"{self.name}-gw"

        self.endpoint_config = None
        self.gateway = IstioGateway(name=self.gateway_name, namespace=self.namespace)
        self.endpoint_config = EndpointConfig(name=self.data.get("spec", {}).get("config"), namespace=self.namespace)

    def create(self) -> "Endpoint":
        self.gateway.create(
            hosts=[self.data.get("spec", {}).get("host")],
            port=8080,
        )

        self.endpoint_config.create(
            endpoint=self.name,
            hosts=[self.data.get("spec", {}).get("host")],
        )

    def update(self) -> "Endpoint":
        self.gateway.update(
            hosts=[self.data.get("spec", {}).get("host")],
            port=8080,
        )

        self.endpoint_config.update(
            endpoint=self.name,
            hosts=[self.data.get("spec", {}).get("host")],
        )
        return self

    def delete(self) -> "Endpoint":
        self.endpoint_config.delete()
        self.gateway.delete()

        return self
