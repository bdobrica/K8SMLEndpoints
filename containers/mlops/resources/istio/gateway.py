from typing import List

from pydantic import BaseModel
from resources.istio.common import GROUP, VERSION, V1Beta1ObjectMeta, V1Beta1Port

GATEWAY_PLURAL: str = "gateways"
GATEWAY_KIND: str = "Gateway"


class V1Beta1GatewaySpecSelector(BaseModel):
    istio: str = "ingressgateway"


class V1Beta1Server(BaseModel):
    hosts: List[str]
    port: V1Beta1Port


class V1Beta1GatewaySpec(BaseModel):
    selector: V1Beta1GatewaySpecSelector
    servers: List[V1Beta1Server]


class V1Beta1Gateway(BaseModel):
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = GATEWAY_KIND
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1GatewaySpec
