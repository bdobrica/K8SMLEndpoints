from kubernetes import client as K8SClient
from resources.custom_resource import CustomResource
from resources.model_deployment import ModelDeployment
from resources.persistent_storage import PersistentStorage


class Model(CustomResource):
    INIT_IMAGE = "quay.io/bdobrica/ml-operator-tools:model-init-latest"

    def __init__(self, name: str, namespace: str = "default"):
        super().__init__(name=name, plural="machinelearningmodels", namespace=namespace)

    def create_storage(self, uid: str = "", size: str = "1Gi", path: str = "/data") -> PersistentStorage:
        api = K8SClient.CoreV1Api()

        name = self.name if uid == "" else f"{self.name}-{uid}"
        pv_body = K8SClient.V1PersistentVolume(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{name}-pv",
                labels={
                    "type": "local",
                    "namespace": self.namespace,
                    "component": name,
                },
            ),
            spec=K8SClient.V1PersistentVolumeSpec(
                storage_class_name="manual",
                capacity={"storage": size},
                access_modes=["ReadWriteOnce"],
                host_path=K8SClient.V1HostPathVolumeSource(path=path),
            ),
        )
        pv = api.create_persistent_volume(body=pv_body)

        pvc_body = K8SClient.V1PersistentVolumeClaim(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{name}-pvc",
                namespace=self.namespace,
            ),
            spec=K8SClient.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=K8SClient.V1ResourceRequirements(requests={"storage": size}),
                selector=K8SClient.V1LabelSelector(
                    match_labels={
                        "namespace": self.namespace,
                        "component": name,
                    }
                ),
            ),
        )
        pvc = api.create_namespaced_persistent_volume_claim(namespace=self.namespace, body=pvc_body)
        return pv, pvc

    def create_deployment(
        self, uid: str = "", instances: int = 1, cpus: str = "1", memory: str = "1Gi"
    ) -> K8SClient.V1Deployment:
        api = K8SClient.AppsV1Api()

        name = self.name if uid == "" else f"{self.name}-{uid}"
        deployment = K8SClient.V1Deployment(
            metadata=K8SClient.V1ObjectMeta(
                name=name,
                namespace=self.namespace,
            ),
            spec=K8SClient.V1DeploymentSpec(
                replicas=instances,
                selector=K8SClient.V1LabelSelector(
                    match_labels={
                        "app": name,
                    }
                ),
                strategy=K8SClient.V1DeploymentStrategy(
                    type="RollingUpdate",
                ),
                template=K8SClient.V1PodTemplateSpec(
                    metadata=K8SClient.V1ObjectMeta(
                        labels={
                            "app": name,
                        }
                    ),
                    spec=K8SClient.V1PodSpec(
                        init_containers=K8SClient.V1Container(
                            image=self.INIT_IMAGE,
                            name=f"{name}-init",
                            env=[
                                K8SClient.V1EnvVar(
                                    name="MODEL_URL",
                                    value=self.data.get("spec", {}).get("artifact", ""),
                                ),
                                K8SClient.V1EnvVar(
                                    name="MODEL_PATH",
                                    value="/opt/ml",
                                ),
                            ],
                            volume_mounts=[
                                K8SClient.V1VolumeMount(
                                    name=f"{name}-storage",
                                    mount_path="/opt/ml",
                                    read_only=True,
                                )
                            ],
                        ),
                        containers=[
                            K8SClient.V1Container(
                                name=name,
                                image=self.data.get("spec", {}).get("image", ""),
                                resources=K8SClient.V1ResourceRequirements(
                                    limits={
                                        "cpu": cpus,
                                        "memory": memory,
                                    },
                                    requests={
                                        "cpu": cpus,
                                        "memory": memory,
                                    },
                                ),
                                volume_mounts=[
                                    K8SClient.V1VolumeMount(
                                        name=f"{name}-storage",
                                        mount_path="/opt/ml",
                                    ),
                                ],
                            ),
                        ],
                        volumes=[
                            K8SClient.V1Volume(
                                name=f"{name}-storage",
                                persistent_volume_claim=K8SClient.V1PersistentVolumeClaimVolumeSource(
                                    claim_name=f"{name}-pvc",
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        )
        return api.create_namespaced_deployment(namespace=self.namespace, body=deployment)

    def create_service(self, uid: str = "") -> K8SClient.V1Service:
        api = K8SClient.CoreV1Api()

        name = self.name if uid == "" else f"{self.name}-{uid}"
        service = K8SClient.V1Service(
            metadata=K8SClient.V1ObjectMeta(
                name=name,
                namespace=self.namespace,
            ),
            spec=K8SClient.V1ServiceSpec(
                type="ClusterIP",
                selector={
                    "app": name,
                },
                ports=[
                    K8SClient.V1ServicePort(
                        port=8080,
                        protocol="TCP",
                        target_port=8080,
                    ),
                ],
            ),
        )
        return api.create_namespaced_service(namespace=self.namespace, body=service)

    def create(
        self,
        uid: str = "",
        instances: int = 1,
        cpus: str = "1",
        memory: str = "1Gi",
        size: str = "1Gi",
        path: str = "/data",
    ) -> ModelDeployment:
        storage = self.create_storage(uid, size, path)
        deployment = self.create_deployment(uid, instances, cpus, memory)
        service = self.create_service(uid)

        return ModelDeployment(
            storage=storage,
            deployment=deployment,
            service=service,
        )
