from kubernetes import client as K8SClient


class ModelService:
    def __init__(self, name: str, version: str, namespace: str) -> None:
        self.name = name
        self.version = version
        self.namespace = namespace

        self.service = None

    def create(self) -> "ModelService":
        api = K8SClient.CoreV1Api()

        service = K8SClient.V1Service(
            metadata=K8SClient.V1ObjectMeta(
                name=f"{self.name}-{self.version}",
                namespace=self.namespace,
            ),
            spec=K8SClient.V1ServiceSpec(
                type="ClusterIP",
                selector={
                    "app": self.name,
                    "version": self.version,
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
        self.service = api.create_namespaced_service(namespace=self.namespace, body=service)
        return self
