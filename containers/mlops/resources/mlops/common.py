from typing import Dict

from pydantic import BaseModel

GROUP: str = "blue.intranet"
VERSION: str = "v1beta1"


class V1Beta1ObjectMeta:
    name: str
    namespace: str
    labels: Dict[str, str] = {}
    finalizers: Dict[str, str] = {}
