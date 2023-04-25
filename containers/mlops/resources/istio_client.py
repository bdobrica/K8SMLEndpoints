from typing import List, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel


class V1Beta1Port(BaseModel):
    name: str = "http"
    number: int
    protocol: str = "HTTP"


class V1Beta1ObjectMeta(BaseModel):
    name: str
    namespace: str
    labels: dict = {}


class V1Beta1Route(BaseModel):
    host: str
    port: V1Beta1Port
    weight: int


class V1Beta1Destination(BaseModel):
    route: List[V1Beta1Route]


class V1Beta1VirtualServiceSpec(BaseModel):
    gateways: List[str]
    hosts: List[str]
    http: List[V1Beta1Destination]


class V1Beta1VirtualService(BaseModel):
    apiVersion: str = "networking.istio.io/v1beta1"
    kind: str = "VirtualService"
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1VirtualServiceSpec


class V1Beta1Server(BaseModel):
    hosts: List[str]
    port: V1Beta1Port


class V1Beta1GatewaySelector(BaseModel):
    istio: str = "ingressgateway"


class V1Beta1GatewaySpec(BaseModel):
    selector: V1Beta1GatewaySelector
    servers: List[V1Beta1Server]


class V1Beta1Gateway(BaseModel):
    apiVersion: str = "networking.istio.io/v1beta1"
    kind: str = "Gateway"
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1GatewaySpec


class V1Beta1Api(BaseModel):
    group: str = "networking.istio.io"
    version: str = "v1beta1"
    name: str
    namespace: str
    api: K8SClient.CustomObjectsApi = K8SClient.CustomObjectsApi()

    def create_namespaced_virtual_service(self, namespace: str, body: Union[V1Beta1VirtualService, dict]) -> dict:
        return self.api.create_namespaced_custom_object(
            group=self.group,
            version=self.version,
            namespace=namespace,
            plural="virtualservices",
            body=body.dict() if isinstance(body, V1Beta1VirtualService) else body,
        )

    def create_namespaced_gateway(self, namespace: str, body: Union[V1Beta1Gateway, dict]) -> dict:
        return self.api.create_namespaced_custom_object(
            group=self.group,
            version=self.version,
            namespace=namespace,
            plural="gateways",
            body=body.dict() if isinstance(body, V1Beta1Gateway) else body,
        )
