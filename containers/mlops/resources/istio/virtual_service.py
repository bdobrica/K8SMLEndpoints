from typing import List

from pydantic import BaseModel
from resources.istio.common import GROUP, VERSION, V1Beta1ObjectMeta, V1Beta1Port

VIRTUAL_SERVICE_PLURAL: str = "virtualservices"
VIRTUAL_SERVICE_KIND: str = "VirtualService"


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
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = VIRTUAL_SERVICE_KIND
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1VirtualServiceSpec
