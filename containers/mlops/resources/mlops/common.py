from enum import Enum
from typing import Dict, List

from pydantic import BaseModel

GROUP: str = "blue.intranet"
VERSION: str = "v1alpha1"


class V1Alpha1ObjectMeta:
    name: str
    namespace: str
    labels: Dict[str, str] = {}
    finalizers: List[str] = {}


class V1Alpha1Status(BaseModel):
    apiVersion: str
    kind: str = "Status"
    metadata: dict = {}
    status: str
    details: dict = {}


class V1Alpha1List(BaseModel):
    apiVersion: str
    kind: str
    metadata: dict = {}
    items: list = []
    resourceVersion: str = ""


class V1Alpha1State(str, Enum):
    AVAILABLE = "available"
    CREATING = "creating"
    UPDATING = "updating"
    DELETING = "deleting"
    FAILED = "failed"
