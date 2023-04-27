from typing import Any, List

from resources.istio_virtual_service import IstioVirtualService
from resources.mlops import client as MLOpsClient
from resources.model import Model
from utils import DiffLine, DiffLineType, get_version


class EndpointConfig:
    def __init__(self, name: str, namespace: str = "default"):
        self.name: str = None
        self.namespace: str = None
        self.body = MLOpsClient.V1Beta1Api().get_namespaced_endpoint_config(name=self.name, namespace=self.namespace)

        self.virtual_service_name: str = None
        self.version: str = None

        self.virtual_service = IstioVirtualService(self.virtual_service_name, self.namespace)
        self.variants: List[Model] = None

    def create(self) -> "EndpointConfig":
        return self

    def update(self, diff: DiffLineType) -> "EndpointConfig":
        return self

    def delete(self) -> "EndpointConfig":
        if not self.body:
            return self

        api = MLOpsClient.V1Beta1Api()
        api.delete_namespaced_endpoint_config(name=self.name, namespace=self.namespace)
        self.body = None
        return self

    def get_attached_endpoint(self) -> List[MLOpsClient.V1Beta1Endpoint]:
        return list(
            filter(
                lambda item: item.spec.config == self.name,
                MLOpsClient.V1Beta1Api().list_namespaced_endpoints(namespace=self.namespace),
            )
        )

    def get_body(self, endpoint: str, hosts: List[str]) -> MLOpsClient.V1Beta1EndpointConfig:
        pass

    def create_handler(self) -> "EndpointConfig":
        self.virtual_service.create()
        for variant in self.variants:
            variant.create()
        return self

    def delete_handler(self) -> "EndpointConfig":
        for variant in self.variants:
            variant.teardown()
        self.variants = []

        self.virtual_service.delete()
        self.virtual_service = None

        return self

    def create(self, endpoint: str, hosts: List[str]) -> "EndpointConfig":
        self.version = get_version()

        virtual_service_destinations = []

        for model in self.get_models():
            variant = Model(
                name=f"{model.get('name')}",
                namespace=self.namespace,
            ).create(
                instances=model.get("instances"),
                cpus=model.get("cpus"),
                memory=model.get("memory"),
                size=model.get("size"),
                path=model.get("path"),
            )
            virtual_service_destinations.append(
                {
                    "host": f"{variant.name}-{variant.version}",
                    "port": 8080,
                    "weight": model.get("weight"),
                }
            )
            self.variants.append(variant)

        self.virtual_service = IstioVirtualService(name=self.virtual_service_name, namespace=self.namespace).create(
            gateway=endpoint, hosts=hosts, destinations=virtual_service_destinations
        )
        return self

    def update(self, diff: DiffLineType) -> "EndpointConfig":
        """
        Update the EndpointConfig. As resources are allocated only when the EndpointConfig is attached to an Endpoint, check if this EndpointConfig is attached to an Endpoint before updating.
        If an endpoint is attached, then:
        - if only weights are being updated, update the weights of the models on the virtual service;
        - if the number of models decreases, delete the models that are no longer needed;
        - if new models are swapped in or added, create new models, add them with the same weights to the virtual service, mark them for monitoring by the daemon, and when all good, delete the old models;
        :param diff: The diff between the old and new versions of the CRD
        """
        if self.get_attached_endpoint() is None:
            return self

        return self

    def add_finalizers(self, finalizers: List[str]) -> "EndpointConfig":
        if isinstance(self.body.metadata.finalizers, list):
            for finalizer in finalizers:
                if finalizer not in self.body.metadata.finalizers:
                    self.body.metadata.finalizers.append(finalizer)
        else:
            self.body.metadata.finalizers = finalizers

        api = MLOpsClient.V1Beta1Api()
        self.body = api.patch_namespaced_endpoint_config(name=self.name, namespace=self.namespace, body=self.body)

        return self

    def remove_finalizers(self, finalizers: List[str]) -> "EndpointConfig":
        if isinstance(self.body.metadata.finalizers, list):
            for finalizer in finalizers:
                if finalizer in self.body.metadata.finalizers:
                    self.body.metadata.finalizers.remove(finalizer)

        api = MLOpsClient.V1Beta1Api()
        self.body = api.patch_namespaced_endpoint_config(name=self.name, namespace=self.namespace, body=self.body)

        return self
