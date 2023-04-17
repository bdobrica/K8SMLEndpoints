from resources.custom_resource import CustomResource
from resources.model import Model


class EndpointConfig(CustomResource):
    def get_models(self):
        model_list = []
        for model in self.data.get("spec", {}).get("models", []):
            model_list.append(
                Model(model.get("model"), self.namespace).set_metadata(
                    {
                        "cpus": model.get("cpus"),
                        "memory": model.get("memory"),
                        "instances": model.get("instances"),
                    }
                )
            )
        return model_list

    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name, "machinelearningendpointconfigs", namespace)
        self.models = self.get_models()
