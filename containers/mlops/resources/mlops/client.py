from typing import Any, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel
from resources.mlops.common import *
from resources.mlops.endpoint import *
from resources.mlops.endpoint_config import *
from resources.mlops.model import *


class V1Beta1Api(BaseModel):
    group: str = GROUP
    version: str = VERSION
    api: K8SClient.CustomObjectsApi = K8SClient.CustomObjectsApi()

    def get_namespaced(self, name: str, namespace: str = "default", plural: str = None) -> Any:
        return self.api.get_namespaced_custom_object(
            self.group,
            self.version,
            namespace,
            plural,
            name,
        )

    def list_namespaced(self, namespace: str = "default", plural: str = None) -> List[Any]:
        return self.api.list_namespaced_custom_object(
            self.group,
            self.version,
            namespace,
            plural,
        )

    def create_namespaced(
        self, namespace: str = "default", body: Union[dict, BaseModel] = None, plural: str = None
    ) -> Any:
        if isinstance(body, BaseModel):
            body = body.dict()

        return self.api.create_namespaced_custom_object(
            self.group,
            self.version,
            namespace,
            plural,
            body,
        )

    def patch_namespaced(
        self, name: str, namespace: str = "default", body: Union[dict, BaseModel] = None, plural: str = None
    ) -> Any:
        if isinstance(body, BaseModel):
            body = body.dict()

        return self.api.patch_namespaced_custom_object(
            self.group,
            self.version,
            namespace,
            plural,
            name,
            body,
        )

    def delete_namespaced(self, name: str, namespace: str = "default", plural: str = None) -> Any:
        return self.api.delete_namespaced_custom_object(
            self.group,
            self.version,
            namespace,
            plural,
            name,
        )

    def get_namespaced_model(self, name: str, namespace: str = "default") -> V1Beta1Model:
        return V1Beta1Model.parse_obj(self.get_namespaced(name, namespace, MODEL_PLURAL))

    def create_namespaced_model(self, namespace: str = "default", body: Union[dict, V1Beta1Model] = None) -> Any:
        return self.create_namespaced(namespace, body, MODEL_PLURAL)

    def patch_namespaced_model(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1Model] = None
    ) -> Any:
        return self.patch_namespaced(name, namespace, body, MODEL_PLURAL)

    def delete_namespaced_model(self, name: str, namespace: str = "default") -> Any:
        return self.delete_namespaced(name, namespace, MODEL_PLURAL)

    def get_namespaced_endpoint_config(self, name: str, namespace: str = "default") -> V1Beta1EndpointConfig:
        return V1Beta1EndpointConfig.parse_obj(self.get_namespaced(name, namespace, ENDPOINT_CONFIG_PLURAL))

    def create_namespaced_endpoint_config(
        self, namespace: str = "default", body: Union[dict, V1Beta1EndpointConfig] = None
    ) -> Any:
        return self.create_namespaced(namespace, body, ENDPOINT_CONFIG_PLURAL)

    def patch_namespaced_endpoint_config(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1EndpointConfig] = None
    ) -> Any:
        return self.patch_namespaced(name, namespace, body, ENDPOINT_CONFIG_PLURAL)

    def delete_namespaced_endpoint_config(self, name: str, namespace: str = "default") -> Any:
        return self.delete_namespaced(name, namespace, ENDPOINT_CONFIG_PLURAL)

    def get_namespaced_endpoint(self, name: str, namespace: str = "default") -> V1Beta1Endpoint:
        return V1Beta1Endpoint.parse_obj(self.get_namespaced(name, namespace, ENDPOINT_PLURAL))

    def list_namespaced_endpoints(self, namespace: str = "default") -> List[V1Beta1Endpoint]:
        return [
            V1Beta1Endpoint.parse_obj(endpoint)
            for endpoint in self.list_namespaced(namespace, ENDPOINT_PLURAL)["items"]
        ]

    def create_namespaced_endpoint(self, namespace: str = "default", body: Union[dict, V1Beta1Endpoint] = None) -> Any:
        return self.create_namespaced(namespace, body, ENDPOINT_PLURAL)

    def patch_namespaced_endpoint(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1Endpoint] = None
    ) -> Any:
        return self.patch_namespaced(name, namespace, body, ENDPOINT_PLURAL)

    def delete_namespaced_endpoint(self, name: str, namespace: str = "default") -> Any:
        return self.delete_namespaced(name, namespace, ENDPOINT_PLURAL)
