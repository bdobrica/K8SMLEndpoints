from typing import Any, Tuple

from resources.endpoint_config import EndpointConfig
from resources.istio_gateway import IstioGateway
from resources.mlops import client as MLOpsClient
from utils import DiffLine, DiffLineType


class Endpoint:
    def __init__(self, name: str, namespace: str = "default"):
        self.name = name
        self.namespace = namespace
        self.body = MLOpsClient.V1Alpha1Api().read_namespaced_endpoint(name=self.name, namespace=self.namespace)

        self.gateway_name = f"{self.name}-gw"
        self.endpoint_config_name = None
        if self.body and self.body.spec:
            self.endpoint_config_name = self.body.spec.config

        self.gateway = IstioGateway(name=self.gateway_name, namespace=self.namespace)
        self.endpoint_config = EndpointConfig(name=self.endpoint_config_name, namespace=self.namespace)

    def get_body(self, config: str, host: str, config_version: str = None) -> MLOpsClient.V1Alpha1Endpoint:
        return MLOpsClient.V1Alpha1Endpoint(
            metadata=MLOpsClient.V1Alpha1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=MLOpsClient.V1Alpha1EndpointSpec(config=config, host=host),
            status=MLOpsClient.V1Alpha1EndpointStatus(endpoint_config_version=config_version),
        )

    def create(self, config: str, host: str) -> "Endpoint":
        if self.body:
            return self

        api = MLOpsClient.V1Alpha1Api()

        body = self.get_body(config=config, host=host)
        self.body = api.create_namespaced_endpoint(namespace=self.namespace, body=body)
        return self

    def delete(self) -> "Endpoint":
        if not self.body or not self.body.metadata or not self.body.metadata.name:
            return self

        api = MLOpsClient.V1Alpha1Api()
        api.delete_namespaced_endpoint(name=self.body.metadata.name, namespace=self.body.metadata.namespace)
        self.body = None
        return self

    def update(self, config: str = None, host: str = None, config_version: str = None) -> "Endpoint":
        if not self.body:
            return self

        api = MLOpsClient.V1Alpha1Api()
        body = self.get_body(
            config=config or self.body.spec.config,
            host=host or self.body.spec.host,
            config_version=config_version or self.body.status.endpoint_config_version,
        )
        self.body = api.patch_namespaced_endpoint(
            name=self.body.metadata.name,
            namespace=self.body.metadata.namespace,
            body=body,
        )
        return self

    def create_handler(self) -> "Endpoint":
        if not self.body:
            return self

        if not self.gateway or not self.gateway.body:
            self.gateway = IstioGateway(name=self.gateway_name, namespace=self.body.metadata.namespace).create(
                labels={"endpoint": self.body.metadata.name},
                hosts=[self.body.spec.host],
                port=8080,
            )

        if (
            not self.endpoint_config
            or not self.endpoint_config.body
            or not self.endpoint_config.body.status
            or self.endpoint_config.body.status.endpoint != self.body.metadata.name
        ):
            self.endpoint_config = EndpointConfig(
                name=self.body.spec.config, namespace=self.body.metadata.namespace
            ).clone(endpoint=self.body.metadata.name)
            self.update(config_version=self.endpoint_config.body.metadata.name)

        return self

    def delete_handler(self) -> "Endpoint":
        self.endpoint_config.delete_handler()
        self.endpoint_config.delete()
        self.gateway.delete()
        return self

    def update_handler(self, diff: Tuple[DiffLineType, ...]) -> "Endpoint":
        self.gateway.update(labels={"endpoint": self.body.metadata.name}, hosts=[self.body.spec.host], port=8080)

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
