from typing import Any, Dict, List, Optional, Tuple

from resources.istio_virtual_service import IstioVirtualService
from resources.mlops import client as MLOpsClient
from resources.model import Model
from utils import DiffLine, DiffLineType, get_version


class EndpointConfig:
    def __init__(self, name: str, namespace: str = "default", version: str = ""):
        self.name: str = name
        self.namespace: str = namespace
        self.version: str = version
        self.named_version: str = f"{self.name}-{self.version}" if self.version else self.name

        self.body = MLOpsClient.V1Alpha1Api().read_namespaced_endpoint_config(
            name=self.named_version,
            namespace=self.namespace,
        )
        if self.body and self.body.status:
            self.name = self.body.status.endpoint_config
            self.version = self.body.status.version

        self.virtual_service_name: str = self.named_version

        self.virtual_service = IstioVirtualService(self.virtual_service_name, self.namespace)

    def get_models(self, models: List[Dict[str, str]] = None) -> List[Model]:
        if not self.body:
            return []

        variants = []
        for n, model in enumerate(models or self.body.spec.models):
            variants.append(
                Model(
                    name=model.model,
                    namespace=self.namespace,
                    version=self.body.status.model_versions[n]
                    if self.body and self.body.status and len(self.body.status.model_versions or []) > n
                    else None,
                )
            )
        return variants

    def get_body(
        self,
        models: List[Dict[str, str]] = None,
        endpoint: Optional[str] = None,
        model_versions: Optional[List[str]] = None,
        state: Optional[str] = None,
    ) -> MLOpsClient.V1Alpha1EndpointConfig:
        return MLOpsClient.V1Alpha1EndpointConfig(
            metadata=MLOpsClient.V1Alpha1ObjectMeta(
                name=self.named_version,
                namespace=self.namespace,
                labels={
                    "endpoint_config": self.name,
                    **({"version": self.version} if self.version else {}),
                },
            ),
            spec=MLOpsClient.V1Alpha1EndpointConfigSpec(
                models=[MLOpsClient.V1Alpha1EndpointConfigModel.parse_obj(model) for model in (models or [])]
            ),
            status=MLOpsClient.V1Alpha1EndpointConfigStatus(
                endpoint=endpoint,
                endpoint_config=self.name,
                version=self.version,
                model_versions=model_versions or [],
                state=state,
            ),
        )

    def get_endpoint(self) -> MLOpsClient.V1Alpha1Endpoint:
        api = MLOpsClient.V1Alpha1Api()

        if self.body and self.body.status:
            return api.read_namespaced_endpoint(name=self.body.status.endpoint, namespace=self.namespace)

        return None

    def create(
        self,
        models: List[Dict[str, str]],
        endpoint: Optional[str] = None,
        model_versions: Optional[List[str]] = None,
        state: Optional[str] = None,
    ) -> "EndpointConfig":
        if self.body:
            return self

        body = self.get_body(
            models=models,
            endpoint=endpoint,
            model_versions=model_versions,
            state=state,
        )
        api = MLOpsClient.V1Alpha1Api()
        self.body = api.create_namespaced_endpoint_config(namespace=self.namespace, body=body)
        return self

    def clone(
        self,
        models: List[Dict[str, str]] = None,
        endpoint: Optional[str] = None,
        model_versions: Optional[List[str]] = None,
        state: Optional[str] = None,
    ):
        return EndpointConfig(
            name=self.name,
            namespace=self.namespace,
            version=get_version(),
        ).create(
            models=models or [model.dict() for model in self.body.spec.models],
            endpoint=endpoint or (self.body.status.endpoint if self.body and self.body.status else None),
            model_versions=model_versions,
            state=state,
        )

    def update(
        self,
        models: List[Dict[str, str]] = None,
        endpoint: Optional[str] = None,
        model_versions: Optional[List[str]] = None,
        state: Optional[str] = None,
    ) -> "EndpointConfig":
        if not self.body or not self.body.status or not self.body.status.version:
            return self

        self.body = self.get_body(
            models=models or self.body.spec.models,
            endpoint=endpoint or self.body.status.endpoint,
            model_versions=model_versions or self.body.status.model_versions,
            state=state or self.body.status.state,
        )
        api = MLOpsClient.V1Alpha1Api()
        self.body = api.patch_namespaced_endpoint_config(name=self.name, namespace=self.namespace, body=self.body)
        return self

    def delete(self) -> "EndpointConfig":
        if not self.body:
            return self

        api = MLOpsClient.V1Alpha1Api()
        api.delete_namespaced_endpoint_config(name=self.name, namespace=self.namespace)
        self.body = None
        return self

    def create_handler(self) -> "EndpointConfig":
        if self.body and self.body.status and self.body.status.model_versions:
            return self

        endpoint = self.get_endpoint()

        model_versions = []
        destinations = []
        for n, model in enumerate(self.get_models()):
            model_ = (
                Model(name=model.name, namespace=self.namespace, version=get_version())
                .create(
                    image=model.body.spec.image,
                    artifact=model.body.spec.artifact,
                    command=model.body.spec.command,
                    args=model.body.spec.args,
                    endpoint=self.body.status.endpoint,
                    endpoint_config=self.body.status.endpoint_config,
                    endpoint_config_version=self.body.metadata.name,
                )
                .create_handler()
            )
            model_versions.append(model_.body.status.version)
            destinations.append(
                {
                    "host": model_.named_version,
                    "port": 8080,
                    "weight": self.body.spec.models[n].weight,
                }
            )

        self.virtual_service.create(
            gateway=self.body.status.endpoint,
            hosts=[endpoint.spec.host],
            destinations=destinations,
        )
        self.update(model_versions=model_versions)

        return self

    def update_handler(self, diff: Optional[Tuple[DiffLineType]] = None) -> "EndpointConfig":
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

        models_diff = DiffLine.from_iter(diff, "change", ("spec", "models"))
        if not models_diff:
            return self

        new_models = self.get_models(models_diff.new_value)
        new_model_names = [model.body.status.model for model in new_models]
        old_models = self.get_models(models_diff.old_value)
        old_model_names = [model.body.status.model for model in old_models]

        for model in old_models:
            if model.name not in new_model_names:
                model.delete_handler().delete()

        model_versions = []
        destinations = []
        for n, model in enumerate(new_models):
            if model.body and model.body.status and model.body.status.model in old_model_names:
                model_versions.append(model.body.status.version)
                destinations.append(
                    {
                        "host": model.named_version,
                        "port": 8080,
                        "weight": self.body.spec.models[n].weight,
                    }
                )
                continue
            model_ = (
                Model(name=model.name, namespace=self.namespace, version=get_version())
                .create(
                    image=model.body.spec.image,
                    artifact=model.body.spec.artifact,
                    command=model.body.spec.command,
                    args=model.body.spec.args,
                    endpoint=self.body.status.endpoint,
                    endpoint_config=self.body.status.endpoint_config,
                    endpoint_config_version=self.body.status.version,
                )
                .create_handler()
            )
            model_versions.append(model_.body.status.version)
            destinations.append(
                {
                    "host": model_.named_version,
                    "port": 8080,
                    "weight": self.body.spec.models[n].weight,
                }
            )

        self.virtual_service.update(
            gateway=endpoint.name,
            hosts=[endpoint.spec.host],
            destinations=destinations,
        )
        self.update(model_versions=model_versions)

        return self

    def delete_handler(self) -> "EndpointConfig":
        for model in self.get_models():
            model.delete()

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

        api = MLOpsClient.V1Alpha1Api()
        self.body = api.patch_namespaced_endpoint_config(name=self.name, namespace=self.namespace, body=self.body)

        return self

    def remove_finalizers(self, finalizers: List[str]) -> "EndpointConfig":
        if isinstance(self.body.metadata.finalizers, list):
            for finalizer in finalizers:
                if finalizer in self.body.metadata.finalizers:
                    self.body.metadata.finalizers.remove(finalizer)

        api = MLOpsClient.V1Alpha1Api()
        self.body = api.patch_namespaced_endpoint_config(name=self.name, namespace=self.namespace, body=self.body)

        return self
