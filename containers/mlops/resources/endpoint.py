from resources.custom_resource import CustomResource
from resources.endpoint_config import EndpointConfig


class Endpoint(CustomResource):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name, "machinelearningendpoints", namespace)
        self.config = EndpointConfig(self.data.get("spec", {}).get("config"), self.namespace).set_metadata(
            {"endpoint": self.name}
        )

    def create(self):
        pass
