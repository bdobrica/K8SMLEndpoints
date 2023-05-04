from typing import List, Optional

from pydantic import BaseModel
from resources.mlops.common import GROUP, VERSION, V1Alpha1ObjectMeta, V1Alpha1State

ENDPOINT_CONFIG_PLURAL: str = "machinelearningendpointconfigs"
ENDPOINT_CONFIG_KIND: str = "MachineLearningEndpointConfig"


class V1Alpha1EndpointConfigModel(BaseModel):
    model: str
    weight: float
    cpus: str
    memory: str
    instances: int
    size: str
    path: str


class V1Alpha1EndpointConfigSpec(BaseModel):
    models: Optional[List[V1Alpha1EndpointConfigModel]]

    class Config:
        arbitrary_types_allowed = True


class V1Alpha1EndpointConfigStatus(BaseModel):
    endpoint: Optional[str]
    endpoint_config: Optional[str]
    version: Optional[str]
    model_versions: Optional[List[str]]
    state: Optional[V1Alpha1State]

    class Config:
        arbitrary_types_allowed = True


class V1Alpha1EndpointConfig(BaseModel):
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = ENDPOINT_CONFIG_KIND
    metadata: V1Alpha1ObjectMeta
    spec: V1Alpha1EndpointConfigSpec
    status: Optional[V1Alpha1EndpointConfigStatus]

    class Config:
        arbitrary_types_allowed = True
