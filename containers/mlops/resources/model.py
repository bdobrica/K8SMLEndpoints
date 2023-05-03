from typing import List, Optional, Tuple

from resources.mlops import client as MLOpsClient
from resources.model_deployment import ModelDeployment
from resources.model_service import ModelService
from resources.model_storage import ModelStorage
from utils import DiffLine, DiffLineType, get_version


class Model:
    def __init__(self, name: str, namespace: str = "default", version: str = ""):
        """
        How it works:
        * If the model exists, then we get the model body from the API
        * If only the name is passed, we check the model against the API and if it exists, retrieve the original name
          and version from the status field
        * If the name and the versions are passed, then we use them to search and intialize the model with the name
          {name}-{version}
        """
        self.name: str = name
        self.namespace: str = namespace
        self.version: str = version
        self.named_version: str = f"{self.name}-{self.version}" if self.version else self.name

        self.body = MLOpsClient.V1Alpha1Api().read_namespaced_model(
            name=self.named_version,
            namespace=namespace,
        )
        if self.body:
            self.name = self.body.status.model
            self.version = self.body.status.version

        self.deployment_name: str = self.named_version
        self.service_name: str = self.named_version
        self.storage_name: str = self.named_version

        self.storage = ModelStorage(name=self.storage_name, namespace=self.namespace)
        self.deployment = ModelDeployment(name=self.deployment_name, namespace=self.namespace)
        self.service = ModelService(name=self.service_name, namespace=self.namespace)

    def get_body(
        self,
        image: str,
        artifact: str,
        command: List[str] = None,
        args: List[str] = None,
        endpoint: str = None,
        endpoint_config: str = None,
        endpoint_config_version: str = None,
        state: str = None,
    ) -> MLOpsClient.V1Alpha1Model:
        return MLOpsClient.V1Alpha1Model(
            metadata=MLOpsClient.V1Alpha1ObjectMeta(
                name=self.named_version,
                namespace=self.namespace,
                labels={
                    "model": self.name,
                    "version": self.version,
                },
            ),
            spec=MLOpsClient.V1Alpha1ModelSpec(
                image=image,
                artifact=artifact,
                command=command,
                args=args,
            ),
            status=MLOpsClient.V1Alpha1ModelStatus(
                endpoint=endpoint,
                endpoint_config=endpoint_config,
                endpoint_config_version=endpoint_config_version,
                model=self.name,
                version=self.version,
                state=state,
            ),
        )

    def get_endpoint_config(self) -> MLOpsClient.V1Alpha1EndpointConfig:
        if not any([self.body, self.deployment, self.service, self.storage.pv, self.storage.pvc]):
            return None

        api = MLOpsClient.V1Alpha1Api()
        results = api.list_namespaced_endpoint_configs(
            namespace=self.namespace,
            field_selector=(
                "metadata.name=" f"{self.body.status.endpoint_config}-" f"{self.body.status.endpoint_config_version}"
            ),
        )
        return results[0] if results else None

    def create(
        self,
        image: str,
        artifact: str,
        command: List[str] = None,
        args: List[str] = None,
        endpoint: str = None,
        endpoint_config: str = None,
        endpoint_config_version: str = None,
        state: str = None,
    ) -> "Model":
        if self.body:
            return self

        api = MLOpsClient.V1Alpha1Api()
        body = self.get_body(
            image=image,
            artifact=artifact,
            command=command,
            args=args,
            endpoint=endpoint,
            endpoint_config=endpoint_config,
            endpoint_config_version=endpoint_config_version,
            state=state,
        )
        self.body = api.create_namespaced_model(body=body, namespace=self.namespace)
        return self

    def update(
        self,
        image: str = None,
        artifact: str = None,
        command: List[str] = None,
        args: List[str] = None,
        endpoint: str = None,
        endpoint_config: str = None,
        endpoint_config_version: str = None,
        state: str = None,
    ) -> "Model":
        if not self.body:
            return self

        api = MLOpsClient.V1Alpha1Api()
        body = self.get_body(
            image=image or self.body.spec.image,
            artifact=artifact or self.body.spec.artifact,
            command=command or self.body.spec.command,
            args=args or self.body.spec.args,
            endpoint=endpoint or self.body.status.endpoint,
            endpoint_config=endpoint_config or self.body.status.endpoint_config,
            endpoint_config_version=endpoint_config_version or self.body.status.endpoint_config_version,
            state=state or self.body.status.state,
        )
        self.body = api.patch_namespaced_model(name=self.name, namespace=self.namespace, body=body)
        return self

    def delete(self) -> "Model":
        if not self.body:
            return self

        api = MLOpsClient.V1Alpha1Api()
        api.delete_namespaced_model(name=self.name, namespace=self.namespace)
        self.body = None
        return self

    def create_handler(self) -> "Model":
        endpoint_config = self.get_endpoint_config()
        if not endpoint_config:
            return self

        model_data = None
        for model in endpoint_config.spec.models:
            if model.model == self.body.status.model:
                model_data = model
                break

        if not model_data:
            return self

        self.storage.create(
            size=model_data.size,
            path=model_data.path,
        )
        self.deployment.create(
            image=self.body.spec.image,
            artifact=self.body.spec.artifact,
            command=self.body.spec.command,
            args=self.body.spec.args,
            instances=model_data.instances,
            cpus=model_data.cpus,
            memory=model_data.memory,
        )
        self.service.create()
        return self

    def update_handler(self, diff: Optional[Tuple[DiffLineType, ...]] = None) -> "Model":
        """
        Some changes should trigger a redeployment (version change)
        - create a copy of the main object with a different version (in k8s, that's why kopf doesn't handle create for this objects)
        - deploy the new object (create attached resources)
        - add finalizers to the main object
        - delete the main object
        - check if the new object is ready, and if so, remove the finalizers on the main object
        - the method should return a reference to the new object
        Changes that might trigger a redeployment:
        - image
        - artifact
        - command
        - args
        - path
        Also, this handler should receive diff objects
        """
        if not self.body or not self.storage or not self.deployment:
            return self

        image = DiffLine.from_iter(diff, "change", ("spec", "image"))
        artifact = DiffLine.from_iter(diff, "change", ("spec", "artifact"))
        command = DiffLine.from_iter(diff, ["add", "change"], ("spec", "command"))
        args = DiffLine.from_iter(diff, ["add", "change"], ("spec", "args"))

        if artifact:
            new_model = (
                Model(name=self.body.metadata.labels["model"], namespace=self.namespace, version=get_version())
                .create(
                    image=self.body.spec.image,
                    artifact=self.body.spec.artifact,
                    command=self.body.spec.command,
                    args=self.body.spec.args,
                    endpoint=self.body.status.endpoint,
                    endpoint_config=self.body.status.endpoint_config,
                    endpoint_config_version=self.body.status.endpoint_config_version,
                )
                .create_handler(
                    instances=self.deployment.body.spec.replicas,
                    cpus=self.deployment.body.spec.template.spec.containers[0].resources.limits["cpu"],
                    memory=self.deployment.body.spec.template.spec.containers[0].resources.limits["memory"],
                    size=self.storage.pv.body.spec.capacity["storage"],
                    path=self.storage.pv.body.spec.host_path.path,
                )
            )
            self.add_finalizers([new_model.body.metadata.name])
            self.delete()
            return new_model

        if not any([image, command, args]):
            return self

        self.deployment.update(
            image=self.body.spec.image,
            artifact=self.body.spec.artifact,
            command=self.body.spec.command,
            args=self.body.spec.args,
        )

        self.storage.update(
            size=self.storage.pv.body.spec.capacity["storage"],
            path=self.storage.pv.body.spec.host_path.path,
        )
        self.deployment.update(
            image=self.body.spec.image,
            artifact=self.body.spec.artifact,
            command=self.body.spec.command,
            args=self.body.spec.args,
            instances=self.deployment.spec.replicas,
            cpus=self.deployment.spec.template.spec.containers[0].resources.limits["cpu"],
            memory=self.deployment.spec.template.spec.containers[0].resources.limits["memory"],
        )
        return self

    def delete_handler(self):
        self.service.delete()
        self.deployment.delete()
        self.storage.delete()
        return self

    def add_finalizers(self, finalizers: List[str]) -> "Model":
        api = MLOpsClient.V1Alpha1Api()
        for finalizer in finalizers:
            if finalizer not in self.body.metadata.finalizers:
                self.body.metadata.finalizers.append(finalizer)
        self.body = api.update_namespaced_model(name=self.name, namespace=self.namespace, body=self.body)
        return self

    def remove_finalizers(self, finalizers: List[str]) -> "Model":
        api = MLOpsClient.V1Alpha1Api()
        for finalizer in finalizers:
            if finalizer in self.body.metadata.finalizers:
                self.body.metadata.finalizers.remove(finalizer)
        self.body = api.update_namespaced_model(name=self.name, namespace=self.namespace, body=self.body)
        return self
