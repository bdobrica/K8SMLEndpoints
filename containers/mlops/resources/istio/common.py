from typing import Dict, List, Union

from pydantic import BaseModel

GROUP: str = "networking.istio.io"
VERSION: str = "v1beta1"


class V1Beta1ObjectMeta(BaseModel):
    name: str
    namespace: str
    labels: Dict[str] = {}
    finalizers: List[str] = []


class V1Beta1Port(BaseModel):
    name: str = "http"
    number: int
    protocol: str = "HTTP"


class V1Beta1Status(BaseModel):
    apiVersion: str
    kind: str = "Status"
    metadata: dict = {}
    status: str
    details: dict = {}
