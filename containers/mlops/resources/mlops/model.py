from typing import List, Optional

from pydantic import BaseModel
from resources.mlops.common import GROUP, VERSION, V1Beta1ObjectMeta

MODEL_PLURAL: str = "models"
MODEL_KIND: str = "Model"


class V1Beta1ModelSpec(BaseModel):
    image: str
    artifact: Optional[str]
    command: Optional[List[str]]
    args: Optional[List[str]]


class V1Beta1ModelStatus(BaseModel):
    endpoint: Optional[str]
    endpoint_config: Optional[str]
    endpoint_config_version: Optional[str]
    model: Optional[str]
    version: Optional[str]
    state: Optional[str]


class V1Beta1Model(BaseModel):
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = MODEL_KIND
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1ModelSpec
    status: Optional[V1Beta1ModelStatus]
