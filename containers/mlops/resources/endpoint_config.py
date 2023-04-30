from typing import Any, Dict, List, Optional

from resources.istio_virtual_service import IstioVirtualService
from resources.mlops import client as MLOpsClient
from resources.model import Model
from utils import DiffLine, DiffLineType, get_version


class EndpointConfig:
    def __init__(self, name: str, namespace: str = "default", version: str = None):
        self.name: str = name
        self.namespace: str = namespace
        self.version: str = version
        self.named_version: str = f"{self.name}-{self.version}" if self.version else self.name

        self.body = MLOpsClient.V1Beta1Api().read_namespaced_endpoint_config(name=self.name, namespace=self.namespace)
        if self.body:
            self.name = self.body.status.endpoint_config
            self.version = self.body.status.version

        self.virtual_service_name: str = None
        self.version: str = None

        self.virtual_service = IstioVirtualService(self.virtual_service_name, self.namespace)
        self.variants: List[Model] = self.get_variants()

    def get_variants(self) -> List[Model]:
        if not self.body:
            return []

        variants = []
        for n, model in enumerate(self.body.spec.models):
            variants.append(
                Model(
                    name=model.model,
                    namespace=self.namespace,
                    version=self.body.status.model_versions[n] if len(self.body.status.model_versions) > n else None,
                )
            )
        return variants

    def get_body(
        self,
        models: List[Dict[str, str]] = None,
        endpoint: Optional[str] = None,
        model_versions: Optional[List[str]] = None,
        state: Optional[str] = None,
    ) -> MLOpsClient.V1Beta1EndpointConfig:
        return MLOpsClient.V1Beta1EndpointConfig(
            metadata=MLOpsClient.V1Beta1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=MLOpsClient.V1Beta1EndpointConfigSpec(
                models=[MLOpsClient.V1Beta1EndpointConfigModel.parse_obj(model) for model in (models or [])]
            ),
            status=MLOpsClient.V1Beta1EndpointConfigStatus(
                endpoint=endpoint,
                endpoint_config=self.name,
                version=self.version,
                model_versions=model_versions or [],
                state=state,
            ),
        )

    def get_endpoint(self) -> MLOpsClient.V1Beta1Endpoint:
        if not any([self.body, self.virtual_service]):
            return None

        api = MLOpsClient.V1Beta1Api()
        results = api.list_namespaced_endpoints(
            namespace=self.namespace,
            field_selector=(f"metadata.name={self.body.status.endpoint}"),
        )
        return results[0] if results else None

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

    def create_handler(self) -> "EndpointConfig":
        if self.body and self.body.status and self.body.status.model_versions:
            return self

        endpoint = self.get_endpoint()

        variants = []
        destinations = []
        for n, variant in enumerate(self.variants):
            new_variant = (
                Model(name=variant.name, namespace=self.namespace, version=get_version())
                .create(
                    image=variant.body.spec.image,
                    artifact=variant.body.spec.artifact,
                    command=variant.body.spec.command,
                    args=variant.body.spec.args,
                    endpoint=self.body.status.endpoint,
                    endpoint_config=self.body.status.endpoint_config,
                    endpoint_config_version=self.body.status.version,
                )
                .create_handler()
            )
            variants.append(new_variant)
            destinations.append(
                {
                    "host": new_variant.named_version,
                    "port": 8080,
                    "weight": self.body.spec.models[n].weight,
                }
            )

        self.variants = variants

        self.virtual_service.create(
            gateway=self.body.status.endpoint,
            hosts=[endpoint.spec.host],
            destinations=destinations,
        )

        return self

    def update_handler(self, diff: DiffLineType) -> "EndpointConfig":
        """
        Update the EndpointConfig. As resources are allocated only when the EndpointConfig is attached to an Endpoint, check if this EndpointConfig is attached to an Endpoint before updating.
        If an endpoint is attached, then:
        - if only weights are being updated, update the weights of the models on the virtual service;
        - if the number of models decreases, delete the models that are no longer needed;
        - if new models are swapped in or added, create new models, add them with the same weights to the virtual service, mark them for monitoring by the daemon, and when all good, delete the old models;
        :param diff: The diff between the old and new versions of the CRD
        """
        endpoint = self.get_endpoint()
        if not endpoint:
            return self

        return self

    def delete_handler(self) -> "EndpointConfig":
        for variant in self.variants:
            variant.delete()
        self.variants = []

        self.virtual_service.delete()
        self.virtual_service = None

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
