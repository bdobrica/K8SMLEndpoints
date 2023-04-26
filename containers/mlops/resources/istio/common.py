from typing import Dict

from pydantic import BaseModel

GROUP: str = "networking.istio.io"
VERSION: str = "v1beta1"


class V1Beta1ObjectMeta(BaseModel):
    name: str
    namespace: str
    labels: Dict[str] = {}
    finalizers: Dict[str] = {}


class V1Beta1Port(BaseModel):
    name: str = "http"
    number: int
    protocol: str = "HTTP"
