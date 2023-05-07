from typing import List

from pydantic import BaseModel
from resources.istio.common import GROUP, VERSION, V1Beta1ObjectMeta, V1Beta1Port

VIRTUAL_SERVICE_PLURAL: str = "virtualservices"
VIRTUAL_SERVICE_KIND: str = "VirtualService"


class V1Beta1Host(BaseModel):
    """
    HTTP route rule to apply during forwarding.
    @param destination: REQUIRED. Destination uniquely identifies the instances of a service to which the request/connection should be forwarded to.
    @param port: The port on the host that is being addressed. If unspecified, the HTTP port (80) will be used.
    @param weight: REQUIRED. The proportion of traffic to be forwarded to the service version. 0 = 0%, 100 = 100%.
    """

    host: str
    port: V1Beta1Port

    class Config:
        arbitrary_types_allowed = True


class V1Beta1Destination(BaseModel):
    """
    List of HTTP route specifications.
    @param route: A list of HTTP route specifications. Requests matching a route will be forwarded to a specific service version. The route may be terminated at the gateway or it may be forwarded to another destination.
    """

    destination: V1Beta1Host
    weight: int

    class Config:
        arbitrary_types_allowed = True


class V1Beta1Route(BaseModel):
    route: List[V1Beta1Destination]

    class Config:
        arbitrary_types_allowed = True


class V1Beta1VirtualServiceSpec(BaseModel):
    """
    The specification for the virtual service.
    @param gateways: A list of gateways to which this rule applies. A gateway is identified by a string which is the name of the Gateway resource.
    @param hosts: REQUIRED. The destination hosts to which traffic is being sent. Could be a DNS name with wildcard prefix or an IP address.
    @param http: HTTP spec defines the HTTP match conditions and actions for the rule.
    """

    gateways: List[str]
    hosts: List[str]
    http: List[V1Beta1Route]

    class Config:
        arbitrary_types_allowed = True


class V1Beta1VirtualService(BaseModel):
    """
    Istio VirtualService resource description.
    """

    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = VIRTUAL_SERVICE_KIND
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1VirtualServiceSpec

    class Config:
        arbitrary_types_allowed = True
