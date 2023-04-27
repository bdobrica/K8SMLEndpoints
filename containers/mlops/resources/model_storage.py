from pathlib import Path
from typing import Any, List, Optional, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel


class ModelStorage:
    def __init__(self, name: str, namespace: str = "default"):
        self.name = name
        self.namespace = namespace

        api = K8SClient.CoreV1Api()
        try:
            self.pv = api.read_persistent_volume(f"{self.name}-pv")
        except K8SClient.ApiException as err:
            if err.status == 404:
                self.pv = None
            else:
                raise
        try:
            self.pvc = api.read_namespaced_persistent_volume_claim(f"{self.name}-pvc", self.namespace)
        except K8SClient.ApiException as err:
            if err.status == 404:
                self.pvc = None
            else:
                raise

    def get_pv_body(
        self, size: str, path: Union[str, Path], finalizers: List[str] = None
    ) -> K8SClient.V1PersistentVolume:
        if isinstance(path, str):
            path = Path(path)

        return K8SClient.V1PersistentVolume(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{self.name}-pv",
                labels={
                    "type": "local",
                    "namespace": self.namespace,
                    "model": self.name,
                },
                finalizers=finalizers,
            ),
            spec=K8SClient.V1PersistentVolumeSpec(
                storage_class_name="manual",
                capacity={"storage": size},
                access_modes=["ReadWriteOnce"],
                host_path=K8SClient.V1HostPathVolumeSource(path=(path / self.name).as_posix()),
            ),
        )

    def get_pvc_body(self, size: str, finalizers: List[str] = None) -> K8SClient.V1PersistentVolumeClaim:
        return K8SClient.V1PersistentVolumeClaim(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{self.name}-pvc",
                namespace=self.namespace,
                finalizers=finalizers,
            ),
            spec=K8SClient.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=K8SClient.V1ResourceRequirements(requests={"storage": size}),
                selector=K8SClient.V1LabelSelector(
                    match_labels={
                        "type": "local",
                        "namespace": self.namespace,
                        "model": self.name,
                    }
                ),
            ),
        )

    def create(self, size: str, path: Union[str, Path]) -> "ModelStorage":
        if isinstance(path, str):
            path = Path(path)

        api = K8SClient.CoreV1Api()

        if self.pv is None:
            pv_body = self.get_pv_body(size=size, path=path)
            self.pv = api.create_persistent_volume(body=pv_body)

        if self.pvc is None:
            pvc_body = self.get_pvc_body(size=size)
            self.pvc = api.create_namespaced_persistent_volume_claim(namespace=self.namespace, body=pvc_body)
        return self

    def delete(self) -> "ModelStorage":
        api = K8SClient.CoreV1Api()

        if self.pvc is not None:
            api.delete_namespaced_persistent_volume_claim(
                name=f"{self.name}-pvc",
                namespace=self.namespace,
            )
            self.pvc = None
        if self.pv is not None:
            api.delete_persistent_volume(name=f"{self.name}-pv")
            self.pv = None
        return self

    def add_finalizers(self, finalizers: List[str]) -> "ModelStorage":
        return self

    def remove_finalizers(self, finalizers: List[str]) -> "ModelStorage":
        return self
