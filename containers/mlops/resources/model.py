from resources.custom_resource import CustomResource


class Model(CustomResource):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name, "machinelearningmodels", namespace)

    def create(self):
        pass
