from typing import Any, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel
from resources.istio.common import *
from resources.istio.gateway import *
from resources.istio.virtual_service import *


class V1Beta1Api(BaseModel):
    group: str = GROUP
    version: str = VERSION
    api: K8SClient.CustomObjectsApi = K8SClient.CustomObjectsApi()

    def get_namespaced(self, name: str, namespace: str = "default", plural: str = None) -> BaseModel:
        return self.api.get_namespaced_custom_object(
            self.group,
            self.version,
            namespace,
            plural,
            name,
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

    def get_namespaced_gateway(self, name: str, namespace: str = "default") -> V1Beta1Gateway:
        return V1Beta1Gateway.parse_obj(self.get_namespaced(name, namespace, GATEWAY_PLURAL))

    def create_namespaced_gateway(
        self, namespace: str = "default", body: Union[dict, V1Beta1Gateway] = None
    ) -> V1Beta1Gateway:
        return V1Beta1Gateway.parse_obj(self.create_namespaced(namespace, body, GATEWAY_PLURAL))

    def patch_namespaced_gateway(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1Gateway] = None
    ) -> V1Beta1Gateway:
        return V1Beta1Gateway(self.patch_namespaced(name, namespace, body, GATEWAY_PLURAL))

    def delete_namespaced_gateway(self, name: str, namespace: str = "default") -> Any:
        return self.delete_namespaced(name, namespace, GATEWAY_PLURAL)

    def get_namespaced_virtual_service(self, name: str, namespace: str = "default") -> V1Beta1VirtualService:
        return V1Beta1VirtualService.parse_obj(self.get_namespaced(name, namespace, VIRTUAL_SERVICE_PLURAL))

    def create_namespaced_virtual_service(
        self, namespace: str = "default", body: Union[dict, V1Beta1VirtualService] = None
    ) -> V1Beta1VirtualService:
        return V1Beta1VirtualService.parse_obj(self.create_namespaced(namespace, body, VIRTUAL_SERVICE_PLURAL))

    def patch_namespaced_virtual_service(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1VirtualService] = None
    ) -> V1Beta1VirtualService:
        return V1Beta1VirtualService.parse_obj(self.patch_namespaced(name, namespace, body, VIRTUAL_SERVICE_PLURAL))

    def delete_namespaced_virtual_service(self, name: str, namespace: str = "default") -> Any:
        return self.delete_namespaced(name, namespace, VIRTUAL_SERVICE_PLURAL)
