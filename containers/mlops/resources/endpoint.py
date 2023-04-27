from typing import Any, Tuple

from resources.endpoint_config import EndpointConfig
from resources.istio_gateway import IstioGateway
from resources.mlops import client as MLOpsClient
from utils import DiffLine, DiffLineType


class Endpoint:
    def __init__(self, name: str, namespace: str = "default"):
        self.name = name
        self.namespace = namespace
        self.body = MLOpsClient.V1Beta1Api().get_namespaced_endpoint(name=self.name, namespace=self.namespace)

        self.gateway_name = f"{self.name}-gw"
        self.endpoint_config_name = self.body.spec.config

        self.gateway = IstioGateway(name=self.gateway_name, namespace=self.namespace)
        self.endpoint_config = EndpointConfig(name=self.endpoint_config_name, namespace=self.namespace)

    def create(self) -> "Endpoint":
        return self

    def delete(self) -> "Endpoint":
        return self

    def update(self, body: MLOpsClient.V1Beta1Endpoint) -> "Endpoint":
        return self

    def create_handler(self) -> "Endpoint":
        self.gateway.create(hosts=[self.body.spec.host], port=8080)
        self.endpoint_config.create(endpoint=self.name, hosts=[self.body.spec.host])
        return self

    def delete_handler(self) -> "Endpoint":
        self.endpoint_config.delete_handler()
        self.endpoint_config.delete()
        self.gateway.delete()
        return self

    def update_handler(self, diff: Tuple[DiffLineType, ...]) -> "Endpoint":
        self.gateway.update(hosts=[self.body.spec.host], port=8080)

        try:
            endpoint_config_diff = next(
                filter(
                    lambda line: line.action == "change" and line.path == ("spec", "config"),
                    map(
                        lambda line: DiffLine.from_tuple(line),
                        diff,
                    ),
                )
            )
        except StopIteration:
            return self

        endpoint_config = (
            EndpointConfig(name=endpoint_config_diff.new_value, namespace=self.namespace)
            .create()
            .create_handler(endpoint=self.name, hosts=[self.body.spec.host])
        )

        self.endpoint_config.add_finalizers([f"started:{endpoint_config.name}"]).delete()
        self.endpoint_config = endpoint_config
        return self
