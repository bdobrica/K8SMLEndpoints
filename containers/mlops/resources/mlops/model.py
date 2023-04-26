from typing import Dict, List, Union

from pydantic import BaseModel
from resources.mlops.common import GROUP, VERSION, V1Beta1ObjectMeta

MODEL_PLURAL: str = "models"
MODEL_KIND: str = "Model"


class V1Beta1ModelSpec(BaseModel):
    image: str
    artifact: Union[str, None] = None
    command: Union[List[str], None] = None
    args: Union[List[str], None] = None


class V1Beta1Model(BaseModel):
    apiVersion: str = f"{GROUP}/{VERSION}"
    kind: str = MODEL_KIND
    metadata: V1Beta1ObjectMeta
    spec: V1Beta1ModelSpec
