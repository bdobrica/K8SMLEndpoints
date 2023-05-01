from typing import Optional

from pydantic import BaseModel
from resources.mlops.common import GROUP, VERSION, V1Beta1ObjectMeta, V1Beta1State

ENDPOINT_PLURAL: str = "endpoints"
ENDPOINT_KIND: str = "Endpoint"


class V1Beta1EndpointSpec(BaseModel):
    config: str
    host: str


class V1Beta1EndpointStatus(BaseModel):
    endpoint_config_version: Optional[str]
    state: Optional[V1Beta1State]


class V1Beta1Endpoint(BaseModel):
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = ENDPOINT_KIND
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1EndpointSpec
    status: Optional[V1Beta1EndpointStatus]
