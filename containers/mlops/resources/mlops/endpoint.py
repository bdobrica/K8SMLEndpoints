from typing import Optional

from pydantic import BaseModel
from resources.mlops.common import GROUP, VERSION, V1Alpha1ObjectMeta, V1Alpha1State

ENDPOINT_PLURAL: str = "endpoints"
ENDPOINT_KIND: str = "Endpoint"


class V1Alpha1EndpointSpec(BaseModel):
    config: str
    host: str


class V1Alpha1EndpointStatus(BaseModel):
    endpoint_config_version: Optional[str]
    state: Optional[V1Alpha1State]


class V1Alpha1Endpoint(BaseModel):
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = ENDPOINT_KIND
    metadata: V1Alpha1ObjectMeta
    spec: V1Alpha1EndpointSpec
    status: Optional[V1Alpha1EndpointStatus]
