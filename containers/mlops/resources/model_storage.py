from pathlib import Path
from typing import Any, List, Optional, Union

from kubernetes import client as K8SClient
from kubernetes.utils import parse_quantity
from pydantic import BaseModel


class ModelStorage:
    def __init__(self, name: str, namespace: str = "default"):
        self.name = name
        self.namespace = namespace

        self.pv_name = f"{self.name}-pv"
        self.pvc_name = f"{self.name}-pvc"

        self.pv: Optional[K8SClient.V1PersistentVolume] = None
        self.pvc: Optional[K8SClient.V1PersistentVolumeClaim] = None

        api = K8SClient.CoreV1Api()
        try:
            self.pv = api.read_persistent_volume(self.pv_name)
        except K8SClient.ApiException as err:
            if err.status == 404:
                self.pv = None
            else:
                raise
        try:
            self.pvc = api.read_namespaced_persistent_volume_claim(name=self.pv_name, namespace=self.namespace)
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
                name=self.pv_name,
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
                name=self.pvc_name,
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

    def update(self, size: Optional[str] = None) -> "ModelStorage":
        if not self.pv or not self.pvc:
            return self

        if size and parse_quantity(size) > parse_quantity(self.pv.spec.capacity["storage"]):
            self.pv.spec.capacity["storage"] = size
            self.pvc.spec.resources.requests["storage"] = size
            api = K8SClient.CoreV1Api()
            self.pv = api.patch_persistent_volume(name=self.pv.metadata.name, body=self.pv)
            self.pvc = api.patch_namespaced_persistent_volume_claim(
                name=self.pvc.metadata.name,
                namespace=self.pvc.metadata.namespace,
                body=self.pvc,
            )

        return self

    def delete(self) -> "ModelStorage":
        api = K8SClient.CoreV1Api()

        if self.pvc and self.pvc.metadata:
            api.delete_namespaced_persistent_volume_claim(
                name=self.pvc.metadata.name,
                namespace=self.pvc.metadata.namespace,
            )
            self.pvc = None
        if self.pv and self.pvc.metadata:
            api.delete_persistent_volume(name=self.pv.metadata.name)
            self.pv = None
        return self

    def add_finalizers(self, finalizers: List[str]) -> "ModelStorage":
        api = K8SClient.CoreV1Api()
        if self.pv and self.pv.metadata:
            if self.pv.metadata.finalizers is None:
                self.pv.metadata.finalizers = []
            for finalizer in finalizers:
                if finalizer not in self.pv.metadata.finalizers:
                    self.pv.metadata.finalizers.append(finalizer)
            self.pv = api.patch_persistent_volume(name=self.pv.metadata.name, body=self.pv)
        if self.pvc and self.pvc.metadata:
            for finalizer in finalizers:
                if finalizer not in self.pvc.metadata.finalizers:
                    self.pvc.metadata.finalizers.append(finalizer)
            self.pvc = api.patch_namespaced_persistent_volume_claim(
                name=self.pvc.metadata.name,
                namespace=self.pvc.metadata.namespace,
                body=self.pvc,
            )
        return self

    def remove_finalizers(self, finalizers: List[str]) -> "ModelStorage":
        api = K8SClient.CoreV1Api()
        if self.pv and self.pv.metadata and self.pv.metadata.finalizers:
            if self.pv.metadata.finalizers is None:
                self.pv.metadata.finalizers = []
            for finalizer in finalizers:
                if finalizer in self.pv.metadata.finalizers:
                    self.pv.metadata.finalizers.remove(finalizer)
            self.pv = api.patch_persistent_volume(name=self.pv.metadata.name, body=self.pv)
        if self.pvc and self.pvc.metadata and self.pvc.metadata.finalizers:
            for finalizer in finalizers:
                if finalizer in self.pvc.metadata.finalizers:
                    self.pvc.metadata.finalizers.remove(finalizer)
            self.pvc = api.patch_namespaced_persistent_volume_claim(
                name=self.pvc.metadata.name,
                namespace=self.pvc.metadata.namespace,
                body=self.pvc,
            )
        return self
