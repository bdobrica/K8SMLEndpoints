from typing import List

import istio_client as IstioClient
from kubernetes import client as K8SClient
from resources.custom_resource import CustomResource


class IstioGateway(CustomResource):
    def __init__(self, name: str, namespace: str = "default") -> None:
        super().__init__(
            name=name, plural="gateways", namespace=namespace, group="networking.istio.io", version="v1beta1"
        )

    def create(self, hosts: List[str], port: int) -> "IstioGateway":
        if self.data:
            return self.update(hosts=hosts, port=port)

        api = IstioClient.V1Beta1Api()

        gateway_body = IstioClient.V1beta1Gateway(
            metadata=IstioClient.V1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=IstioClient.V1beta1GatewaySpec(
                selector=IstioClient.V1beta1GatewaySpecSelector(istio="ingressgateway"),
                servers=[
                    IstioClient.V1beta1Server(
                        hosts=hosts,
                        port=IstioClient.V1beta1ServerPort(
                            name="http",
                            number=port,
                            protocol="HTTP",
                        ),
                    )
                ],
            ),
        )

        self.data = api.create_namespaced_gateway(
            namespace=self.namespace,
            body=gateway_body,
        ).get("spec", {})

        return self

    def update(self, hosts: List[str], port: int) -> "IstioGateway":
        api = K8SClient.CustomObjectsApi()

        gateway_body = {
            "apiVersion": f"{self.group}/{self.version}",
            "kind": "Gateway",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
            },
            "spec": {
                "selector": {
                    "istio": "ingressgateway",
                },
                "servers": [
                    {
                        "hosts": hosts,
                        "port": {
                            "name": "http",
                            "number": port,
                            "protocol": "HTTP",
                        },
                    },
                ],
            },
        }

        self.data = api.patch_namespaced_custom_object(
            group=self.group,
            version=self.version,
            namespace=self.namespace,
            plural=self.plural,
            name=self.name,
            body=gateway_body,
        ).get("spec", {})

        return self

    def delete(self) -> "IstioGateway":
        if not self.data:
            return self

        api = K8SClient.CustomObjectsApi()

        api.delete_namespaced_custom_object(
            group=self.group,
            version=self.version,
            namespace=self.namespace,
            plural=self.plural,
            name=self.name,
        )
        self.data = {}

        return self
