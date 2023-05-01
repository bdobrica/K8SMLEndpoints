from enum import Enum
from typing import Dict

from pydantic import BaseModel

GROUP: str = "blue.intranet"
VERSION: str = "v1beta1"


class V1Beta1ObjectMeta:
    name: str
    namespace: str
    labels: Dict[str, str] = {}
    finalizers: Dict[str, str] = {}


class V1Beta1Status(BaseModel):
    apiVersion: str
    kind: str = "Status"
    metadata: dict = {}
    status: str
    details: dict = {}


class V1Beta1List(BaseModel):
    apiVersion: str
    kind: str
    metadata: dict = {}
    items: list = []
    resourceVersion: str = ""


class V1Beta1State(str, Enum):
    AVAILABLE = "available"
    CREATING = "creating"
    UPDATING = "updating"
    DELETING = "deleting"
    FAILED = "failed"
