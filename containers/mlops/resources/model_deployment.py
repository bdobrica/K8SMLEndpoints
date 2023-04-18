from dataclasses import dataclass

from kubernetes import client as K8SClient
from resources.persistent_storage import PersistentStorage


@dataclass
class ModelDeployment:
    storage: PersistentStorage
    deployment: K8SClient.V1Deployment
    service: K8SClient.V1Service
