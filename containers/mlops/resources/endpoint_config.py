from typing import Any, List

from kubernetes import client as K8SClient
from resources.custom_resource import CustomResource
from resources.istio_virtual_service import IstioVirtualService
from resources.model import Model
from utils import get_version


class EndpointConfig(CustomResource):
    def get_models(self):
        return [model for model in self.data.get("spec", {}).get("models", [])]

    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name, "machinelearningendpointconfigs", namespace)

        self.virtual_service_name = f"{self.name}-{self.version}-vs"

        self.version: str = None
        self.variants: List[Model] = []
        self.virtual_service: Any = None

    def get_attached_endpoint(self):
        return None

    def create(self, endpoint: str, hosts: List[str]) -> "EndpointConfig":
        api = K8SClient.CustomObjectsApi()

        self.version = get_version()

        virtual_service_routes = []
        virtual_service_body = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": f"{self.name}-{self.version}-vs",
                "namespace": self.namespace,
            },
            "spec": {
                "gateways": [
                    f"{endpoint}",
                ],
                "hosts": hosts,
                "http": [
                    {
                        "route": virtual_service_routes,
                    }
                ],
            },
        }

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

        self.virtual_service.create(
            gateway=endpoint,
            hosts=hosts,
            destinations=virtual_service_destinations,
        )

        return self

    def update(self, diff: dict) -> "EndpointConfig":
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

    def delete(self) -> "EndpointConfig":
        for variant in self.variants:
            variant.delete()

        api = K8SClient.CustomObjectsApi()

        api.delete_namespaced_custom_object(
            group="networking.istio.io",
            version="v1beta1",
            namespace=self.namespace,
            plural="virtualservices",
            name=f"{self.name}-{self.version}-vs",
        )

        return self
