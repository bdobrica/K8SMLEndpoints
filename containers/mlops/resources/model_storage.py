from kubernetes import client as K8SClient


class ModelStorage:
    def __init__(self, name: str, namespace: str, version: str, size: str, path: str):
        self.name = name
        self.namespace = namespace
        self.version = version
        self.size = size
        self.path = path

        self.pv = None
        self.pvc = None

    def create(self) -> "ModelStorage":
        api = K8SClient.CoreV1Api()

        pv_body = K8SClient.V1PersistentVolume(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{self.name}-{self.version}-pv",
                labels={
                    "type": "local",
                    "namespace": self.namespace,
                    "model": self.name,
                    "version": self.version,
                },
            ),
            spec=K8SClient.V1PersistentVolumeSpec(
                storage_class_name="manual",
                capacity={"storage": self.size},
                access_modes=["ReadWriteOnce"],
                host_path=K8SClient.V1HostPathVolumeSource(path=self.path),
            ),
        )
        self.pv = api.create_persistent_volume(body=pv_body)

        pvc_body = K8SClient.V1PersistentVolumeClaim(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{self.name}-{self.version}-pvc",
                namespace=self.namespace,
            ),
            spec=K8SClient.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=K8SClient.V1ResourceRequirements(requests={"storage": self.size}),
                selector=K8SClient.V1LabelSelector(
                    match_labels={
                        "namespace": self.namespace,
                        "component": self.name,
                        "version": self.version,
                    }
                ),
            ),
        )
        self.pvc = api.create_namespaced_persistent_volume_claim(namespace=self.namespace, body=pvc_body)
        return self
