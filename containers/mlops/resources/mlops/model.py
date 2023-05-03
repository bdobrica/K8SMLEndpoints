from typing import List, Optional

from pydantic import BaseModel
from resources.mlops.common import GROUP, VERSION, V1Alpha1ObjectMeta, V1Alpha1State

MODEL_PLURAL: str = "models"
MODEL_KIND: str = "Model"


class V1Alpha1ModelSpec(BaseModel):
    image: str
    artifact: Optional[str]
    command: Optional[List[str]]
    args: Optional[List[str]]


class V1Alpha1ModelStatus(BaseModel):
    endpoint: Optional[str]
    endpoint_config: Optional[str]
    endpoint_config_version: Optional[str]
    model: Optional[str]
    version: Optional[str]
    state: Optional[V1Alpha1State]


class V1Alpha1Model(BaseModel):
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = MODEL_KIND
    metadata: V1Alpha1ObjectMeta
    spec: V1Alpha1ModelSpec
    status: Optional[V1Alpha1ModelStatus]
