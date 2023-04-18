from kubernetes import client as K8SClient
from resources.custom_resource import CustomResource
from resources.endpoint_config import EndpointConfig


class Endpoint(CustomResource):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name, "machinelearningendpoints", namespace)
        self.config = EndpointConfig(self.data.get("spec", {}).get("config"), self.namespace).set_metadata(
            {"endpoint": self.name}
        )

    def create(self):
        models = self.config.create()

        api = K8SClient.CustomObjectsApi()
        body = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "Gateway",
            "metadata": {
                "name": f"{self.name}-gateway",
                "namespace": self.namespace,
            },
            "spec": {
                "selector": {
                    "istio": "ingressgateway",
                },
                "servers": [
                    {
                        "hosts": [self.data.get("spec", {}).get("host")],
                        "port": {
                            "name": "http",
                            "number": 8080,
                            "protocol": "HTTP",
                        },
                    },
                ],
            },
        }
        api.create_namespaced_custom_object(
            group="networking.istio.io", version="v1beta1", namespace=self.namespace, plural="gateways", body=body
        )

        body = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": f"{self.name}-virtualservice",
                "namespace": self.namespace,
            },
            "spec": {
                "gateways": [
                    f"{self.name}-gateway",
                ],
                "hosts": [
                    self.data.get("spec", {}).get("host"),
                ],
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": model.name,
                                    "port": {
                                        "number": 8080,
                                    },
                                    "weight": model.weight,
                                }
                                for model in models
                            }
                        ]
                    }
                ],
            },
        }
        api.create_namespaced_custom_object(
            group="networking.istio.io",
            version="v1beta1",
            namespace=self.namespace,
            plural="virtualservices",
            body=body,
        )
