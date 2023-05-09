from typing import Any, Dict, List, Optional, Tuple

from resources.istio_virtual_service import IstioVirtualService
from resources.mlops import client as MLOpsClient
from resources.model import Model
from utils import DiffLine, DiffLineType, get_version


class EndpointConfig:
    """
    The EndpointConfig class is a handling model configuration for an endpoint. It is used to create, update, and delete
    endpoint configs. It is also used to retrieve information about the endpoint config and the models associated with
    it.

    An endpoint config allows specifying multiple models to be used for an endpoint by providing for each the weight of
    the traffic to be routed to it. An also allows specifying each model's resource requirements and the number of
    replicas to be used for each model.

    The underlying Kubernetes resource used for the endpoint config is an Istio VirtualService that provides the routing
    information for the endpoint.
    """

    def __init__(self, name: str, namespace: str = "default", version: str = "") -> None:
        """
        Initialize an EndpointConfig object by providing a name and namespace. If the endpoint config already exists,
        the information describing it is retrieved from the API and stored in the body attribute. If the endpoint config
        does not exist, the body attribute is set to None.

        :param name: The name of the endpoint config.
        :param namespace: The namespace of the endpoint config. Defaults to the "default" namespace.
        :param version: The version of the endpoint config. If the version is provided, the name is set to the
        name-version format. This is used when creating a new instance.
        """
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
        """
        Get the models associated with the endpoint config. If the endpoint config does not exist, an empty list is
        returned. You can optionally provide a list of models to use instead of the models associated with the endpoint
        config.

        :param models: A list of models to use instead of the models associated with the endpoint config.
        :return: A list of Model objects.
        """
        if not self.body:
            return []

        variants = []
        for n, model in enumerate(models or self.body.spec.models):
            variants.append(
                Model(
                    name=self.body.status.model_versions[n]
                    if self.body and self.body.status and len(self.body.status.model_versions or []) > n
                    else model.model,
                    namespace=self.namespace,
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
        """
        Method used to create the Kubernetes API request body for creating/updating an endpoint config.

        :param models: A list of models to use instead of the models associated with the endpoint config. Each model is
        a dictionary with the keys "model", "weight", "cpus", "memory", and "instances".
        :param endpoint: The name of the endpoint that the endpoint config is associated with.
        :param model_versions: A list of model versions for each model provided in the models parameter. The order of
        the model versions must match the order of the models.
        :param state: The state of the endpoint config.
        :return: A Kubernetes API request body for creating/updating an endpoint config.
        """
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

    def get_endpoint(self) -> Optional[MLOpsClient.V1Alpha1Endpoint]:
        """
        Get the endpoint associated with the endpoint config. If the endpoint config does not exist, None is returned.
        :return: An Endpoint object.
        """
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
        """
        Method used for creating the EndpointConfig associated kubernetes resource. The method does not create any
        other kubernetes resources such as the endpoint or the virtual service. The method returns a reference to self.
        For creating associated resources, use the create_handler method.

        :param models: A list of models to use instead of the models associated with the endpoint config. Each model is
        a dictionary with the keys "model", "weight", "cpus", "memory", and "instances".
        :param endpoint: The name of the endpoint that the endpoint config is associated with.
        :param model_versions: A list of model versions for each model provided in the models parameter. The order of
        the model versions must match the order of the models.
        :param state: The state of the endpoint config.
        :return: An EndpointConfig object (reference to self for easy chaining).
        """
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
        """
        This method is intended on a kubernetes resource that already exists. It will create a new kubernetes resource
        with the name of the current resource appended with a new version string. Parts of the original (self) resource
        can be overridden by providing the appropriate parameters. It does not create any associated resources.

        :param models: A list of models to use instead of the models associated with the endpoint config. Each model is
        a dictionary with the keys "model", "weight", "cpus", "memory", and "instances".
        :param endpoint: The name of the endpoint that the endpoint config is associated with.
        :param model_versions: A list of model versions for each model provided in the models parameter. The order of
        the model versions must match the order of the models.
        :param state: The state of the endpoint config.
        :return: An EndpointConfig object reference to the new resource.
        """
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
        """
        Method used for updating the EndpointConfig associated kubernetes resource. The method does not update any
        other kubernetes resources such as the endpoint or the virtual service. The method returns a reference to self.
        For updating associated resources, use the update_handler method.

        :param models: A list of models to use instead of the models associated with the endpoint config. Each model is
        a dictionary with the keys "model", "weight", "cpus", "memory", and "instances".
        :param endpoint: The name of the endpoint that the endpoint config is associated with.
        :param model_versions: A list of model versions for each model provided in the models parameter. The order of
        the model versions must match the order of the models.
        :param state: The state of the endpoint config.
        :return: An EndpointConfig object (reference to self for easy chaining).
        """
        if not self.body or not self.body.status or not self.body.status.version:
            return self

        body = self.get_body(
            models=models or self.body.spec.models,
            endpoint=endpoint or self.body.status.endpoint,
            model_versions=model_versions or self.body.status.model_versions,
            state=state or self.body.status.state,
        )
        api = MLOpsClient.V1Alpha1Api()
        self.body = api.patch_namespaced_endpoint_config(
            name=self.body.metadata.name, namespace=self.body.metadata.namespace, body=body
        )
        return self

    def delete(self) -> "EndpointConfig":
        """
        Method used for deleting the EndpointConfig associated kubernetes resource. The method does not delete any
        other kubernetes resources such as the endpoint or the virtual service. The method returns a reference to self.
        The return object will have the body attribute set to None.
        Note: As you might probably don't want to delete the endpoint config without deleting the associated resources,
        use add_finalizer before deleting the endpoint config and remove_finalizer after deleting the associated
        resources.

        :return: An EndpointConfig object (reference to self for easy chaining).
        """
        if not self.body:
            return self

        api = MLOpsClient.V1Alpha1Api()
        api.delete_namespaced_endpoint_config(name=self.body.metadata.name, namespace=self.body.metadata.namespace)
        self.body = None
        return self

    def create_handler(self) -> "EndpointConfig":
        """
        Method used for creating associated resources. The method returns a reference to self.
        An endpoint config has the following associated resources:
        - an Istio virtual service

        :return: An EndpointConfig object (reference to self for easy chaining).
        """
        if self.body and self.body.status and self.body.status.model_versions:
            return self

        endpoint = self.get_endpoint()

        print("detected endpoint", endpoint)

        model_versions = []
        destinations = []
        for n, model in enumerate(self.get_models()):
            model_ = Model(name=model.name, namespace=self.namespace, version=get_version()).create(
                image=model.body.spec.image,
                artifact=model.body.spec.artifact,
                command=model.body.spec.command,
                args=model.body.spec.args,
                endpoint=self.body.status.endpoint,
                endpoint_config=self.body.status.endpoint_config,
                endpoint_config_version=self.body.metadata.name,
            )
            model_versions.append(model_.body.metadata.name)
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

        :param diff: The diff between the old and new versions of the CRD as a list of DiffLine objects (see utils.py).
        :return: An EndpointConfig object (reference to self for easy chaining).
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
                model.delete()

        model_versions = []
        destinations = []
        for n, model in enumerate(new_models):
            if model.body and model.body.status and model.body.status.model in old_model_names:
                model_versions.append(model.body.metadata.name)
                destinations.append(
                    {
                        "host": model.named_version,
                        "port": 8080,
                        "weight": self.body.spec.models[n].weight,
                    }
                )
                continue
            model_ = Model(name=model.body.status.model, namespace=self.namespace, version=get_version()).create(
                image=model.body.spec.image,
                artifact=model.body.spec.artifact,
                command=model.body.spec.command,
                args=model.body.spec.args,
                endpoint=self.body.status.endpoint,
                endpoint_config=self.body.status.endpoint_config,
                endpoint_config_version=self.body.status.version,
            )
            model_versions.append(model_.body.metadata.name)
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
        """
        Delete the EndpointConfig. Method intended to be used with kopf.on.delete.

        :return: An EndpointConfig object (reference to self for easy chaining).
        """
        for model in self.get_models():
            model.delete()

        self.virtual_service.delete()
        self.virtual_service = None

        return self

    def add_finalizers(self, finalizers: List[str]) -> "EndpointConfig":
        """
        Add finalizers to the EndpointConfig. While the finalizers are present, the EndpointConfig cannot be deleted
        even if the deletion of the EndpointConfig is requested. When the finalizers are removed, the EndpointConfig
        will be deleted.

        :param finalizers: A list of finalizers to add (simple strings).
        :return: An EndpointConfig object (reference to self for easy chaining).
        """
        if isinstance(self.body.metadata.finalizers, list):
            for finalizer in finalizers:
                if finalizer not in self.body.metadata.finalizers:
                    self.body.metadata.finalizers.append(finalizer)
        else:
            self.body.metadata.finalizers = finalizers

        api = MLOpsClient.V1Alpha1Api()
        self.body = api.patch_namespaced_endpoint_config(
            name=self.body.metadata.name, namespace=self.body.metadata.namespace, body=self.body
        )

        return self

    def remove_finalizers(self, finalizers: List[str]) -> "EndpointConfig":
        """
        Remove finalizers from the EndpointConfig. While the finalizers are present, the EndpointConfig cannot be
        deleted even if the deletion of the EndpointConfig is requested. When the finalizers are removed, the
        EndpointConfig will be deleted.

        :param finalizers: A list of finalizers to remove (simple strings).
        :return: An EndpointConfig object (reference to self for easy chaining).
        """
        if isinstance(self.body.metadata.finalizers, list):
            for finalizer in finalizers:
                if finalizer in self.body.metadata.finalizers:
                    self.body.metadata.finalizers.remove(finalizer)

        api = MLOpsClient.V1Alpha1Api()
        self.body = api.patch_namespaced_endpoint_config(
            name=self.body.metadata.name, namespace=self.body.metadata.namespace, body=self.body
        )

        return self
