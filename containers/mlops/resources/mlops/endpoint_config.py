from typing import List

from pydantic import BaseModel
from resources.mlops.common import GROUP, VERSION, V1Beta1ObjectMeta

ENDPOINT_CONFIG_PLURAL: str = "endpointconfigs"
ENDPOINT_CONFIG_KIND: str = "EndpointConfig"


class V1Beta1EndpointConfigModel(BaseModel):
    model: str
    weight: float
    cpus: str
    memory: str
    instances: int
    size: str
    path: str


class V1Beta1EndpointConfigSpec(BaseModel):
    models: List[V1Beta1EndpointConfigModel]


class V1Beta1EndpointConfig(BaseModel):
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = ENDPOINT_CONFIG_KIND
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1EndpointConfigSpec
