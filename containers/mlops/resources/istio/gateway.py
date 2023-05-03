from typing import Dict, List

from pydantic import BaseModel
from resources.istio.common import GROUP, VERSION, V1Beta1ObjectMeta, V1Beta1Port

GATEWAY_PLURAL: str = "gateways"
GATEWAY_KIND: str = "Gateway"


class V1Beta1Server(BaseModel):
    """
    @param hosts: REQUIRED. A list of hosts exposed by this gateway. At least one host is required. May use * as a wildcard at the start of the hostname.
    @param port: REQUIRED. The port on which the proxy should listen for incoming connections.
    """

    hosts: List[str]
    port: V1Beta1Port

    class Config:
        arbitrary_types_allowed = True


class V1Beta1GatewaySpec(BaseModel):
    """
    The specification for the gateway.
    """

    selector: Dict[str, str]
    servers: List[V1Beta1Server]

    class Config:
        arbitrary_types_allowed = True


class V1Beta1Gateway(BaseModel):
    """
    Istio Gateay resouce description.
    """

    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = GATEWAY_KIND
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1GatewaySpec

    class Config:
        arbitrary_types_allowed = True
