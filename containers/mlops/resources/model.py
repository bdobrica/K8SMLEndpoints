from resources.custom_resource import CustomResource
from resources.model_deployment import ModelDeployment
from resources.model_service import ModelService
from resources.model_storage import ModelStorage
from utils import get_version


class Model(CustomResource):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name=name, plural="machinelearningmodels", namespace=namespace)

        self.image = self.data.get("spec", {}).get("image")
        self.artifact = self.data.get("spec", {}).get("artifact")
        self.command = self.data.get("spec", {}).get("command")

        self.version = None
        self.storage = None
        self.deployment = None
        self.service = None

    def create(self, instances: str, cpus: str, memory: str, size: str, path: str) -> "Model":
        self.version = get_version()
        self.storage = ModelStorage(
            name=self.name, namespace=self.namespace, version=self.version, size=size, path=path
        ).create()
        self.deployment = ModelDeployment(
            name=self.name,
            namespace=self.namespace,
            version=self.version,
            image=self.image,
            artifact=self.artifact,
            instances=instances,
            cpus=cpus,
            memory=memory,
        ).create()
        self.service = ModelService(name=self.name, namespace=self.namespace, version=self.version).create()
        return self

    def update(self, instances: str, cpus: str, memory: str, size: str, path: str) -> "Model":
        return self

    def delete(self):
        self.service.delete()
        self.deployment.delete()
        self.storage.delete()
        return self
