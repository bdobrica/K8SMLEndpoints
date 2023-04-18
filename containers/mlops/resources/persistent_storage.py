from dataclasses import dataclass

from kubernetes import client as K8SClient


@dataclass
class PersistentStorage:
    pv: K8SClient.V1PersistentVolume
    pvc: K8SClient.V1PersistentVolumeClaim
