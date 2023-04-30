from typing import Any, Optional, Type, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel
from resources.istio.common import *
from resources.istio.gateway import *
from resources.istio.virtual_service import *


class V1Beta1Api(BaseModel):
    group: str = GROUP
    version: str = VERSION
    api: K8SClient.CustomObjectsApi = K8SClient.CustomObjectsApi()

    def read_namespaced(
        self,
        name: str,
        namespace: str = "default",
        plural: str = None,
        format: Type[BaseModel] = None,
    ) -> Optional[Union[BaseModel, dict]]:
        try:
            result = self.api.get_namespaced_custom_object(
                self.group,
                self.version,
                namespace,
                plural,
                name,
            )
        except K8SClient.ApiException as err:
            if err.status == 404:
                return None
            else:
                raise

        if format:
            return format.parse_obj(result)

        return result

    def create_namespaced(
        self,
        namespace: str = "default",
        body: Union[dict, BaseModel] = None,
        plural: str = None,
        format: Type[BaseModel] = None,
    ) -> Union[BaseModel, dict]:
        if isinstance(body, BaseModel):
            body = body.dict()

        try:
            result = self.api.create_namespaced_custom_object(
                self.group,
                self.version,
                namespace,
                plural,
                body,
            )
        except K8SClient.ApiException as result:
            raise

        if format:
            return format.parse_obj(result)

        return result

    def patch_namespaced(
        self,
        name: str,
        namespace: str = "default",
        body: Union[dict, BaseModel] = None,
        plural: str = None,
        format: Type[BaseModel] = None,
    ) -> Union[BaseModel, dict]:
        if isinstance(body, BaseModel):
            body = body.dict()

        try:
            result = self.api.patch_namespaced_custom_object(
                self.group,
                self.version,
                namespace,
                plural,
                name,
                body,
            )
        except K8SClient.ApiException as result:
            raise

        if format:
            return format.parse_obj(result)

        return result

    def delete_namespaced(
        self,
        name: str,
        namespace: str = "default",
        plural: str = None,
    ) -> Optional[V1Beta1Status]:
        try:
            result = self.api.delete_namespaced_custom_object(
                self.group,
                self.version,
                namespace,
                plural,
                name,
            )
        except K8SClient.ApiException as result:
            if result.status == 404:
                return None
            else:
                raise

        return V1Beta1Status.parse_obj(result)

    def read_namespaced_gateway(self, name: str, namespace: str = "default") -> Optional[V1Beta1Gateway]:
        return self.read_namespaced(name, namespace, GATEWAY_PLURAL, V1Beta1Gateway)

    def create_namespaced_gateway(
        self, namespace: str = "default", body: Union[dict, V1Beta1Gateway] = None
    ) -> V1Beta1Gateway:
        return self.create_namespaced(namespace, body, GATEWAY_PLURAL, V1Beta1Gateway)

    def patch_namespaced_gateway(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1Gateway] = None
    ) -> V1Beta1Gateway:
        return self.patch_namespaced(name, namespace, body, GATEWAY_PLURAL, V1Beta1Gateway)

    def delete_namespaced_gateway(self, name: str, namespace: str = "default") -> Optional[V1Beta1Status]:
        return self.delete_namespaced(name, namespace, GATEWAY_PLURAL)

    def read_namespaced_virtual_service(self, name: str, namespace: str = "default") -> Optional[V1Beta1VirtualService]:
        return self.read_namespaced(name, namespace, VIRTUAL_SERVICE_PLURAL, V1Beta1VirtualService)

    def create_namespaced_virtual_service(
        self, namespace: str = "default", body: Union[dict, V1Beta1VirtualService] = None
    ) -> V1Beta1VirtualService:
        return self.create_namespaced(namespace, body, VIRTUAL_SERVICE_PLURAL, V1Beta1VirtualService)

    def patch_namespaced_virtual_service(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1VirtualService] = None
    ) -> V1Beta1VirtualService:
        return self.patch_namespaced(name, namespace, body, VIRTUAL_SERVICE_PLURAL, V1Beta1VirtualService)

    def delete_namespaced_virtual_service(self, name: str, namespace: str = "default") -> Optional[V1Beta1Status]:
        return self.delete_namespaced(name, namespace, VIRTUAL_SERVICE_PLURAL)
