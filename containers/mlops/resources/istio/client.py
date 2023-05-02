from typing import Any, Optional, Type, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel
from resources.istio.common import *
from resources.istio.gateway import *
from resources.istio.virtual_service import *


class V1Beta1Api(BaseModel):
    """
    Object for interfacing with the Istio v1beta1 API.
    """

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
        """
        Read a namespaced Istio resource. If the resource doesn't exist, None will be returned.
        @param name: Name of the resource. Required.
        @param namespace: Namespace of the resource. Default value is "default".
        @param plural: Plural kind of the resource.
        @param format: Pydantic model to parse the result into. If not provided, the raw dict will be returned.
        @return: The resource if it exists in dict or pydantic format (if format was passed), None otherwise.
        """
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
        """
        Create a namespaced Istio resource. If the resource doesn't exist,
        @param namespace: Namespace of the resource. Default value is "default".
        @param body: Body of the resource. Required. Should be a dict or Pydantic model.
        @param plural: Plural kind of the resource.
        @param format: Pydantic model to parse the result into. If not provided, the raw dict will be returned.
        @return: The created resource in dict or pydantic format (if format was passed).
        """
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
        """
        Patch a namespaced Istio resource.
        @param name: Name of the resource. Required.
        @param namespace: Namespace of the resource. Default value is "default".
        @param body: Body of the resource. Required. Should be a dict or Pydantic model.
        @param plural: Plural kind of the resource.
        @param format: Pydantic model to parse the result into. If not provided, the raw dict will be returned.
        @return: The patched resource in dict or pydantic format (if format was passed).
        """
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
        """
        Delete a namespaced Istio resource.
        @param name: Name of the resource. Required.
        @param namespace: Namespace of the resource. Default value is "default".
        @param plural: Plural kind of the resource.
        @return: The status of the delete operation, as a pydantic model.
        """
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
        """
        Reads an [Istio gateway](https://istio.io/latest/docs/reference/config/networking/gateway/) resource.
        Returns None if the gateway doesn't exist.
        @param name: Name of the gateway.
        @param namespace: Namespace of the gateway. Default value is "default".
        @return: The gateway resource if it exists, None otherwise.
        """
        return self.read_namespaced(name, namespace, GATEWAY_PLURAL, V1Beta1Gateway)

    def create_namespaced_gateway(
        self, namespace: str = "default", body: Union[dict, V1Beta1Gateway] = None
    ) -> V1Beta1Gateway:
        """
        Creats an Istio gatwey resource and returns the created resource.
        @param namespace: Namespace of the gateway. Default value is "default".
        @param body: Body of the gateway. Should be a dict or Pydantic model.
        @return: The created gateway resource in pydantic format.
        """
        return self.create_namespaced(namespace, body, GATEWAY_PLURAL, V1Beta1Gateway)

    def patch_namespaced_gateway(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1Gateway] = None
    ) -> V1Beta1Gateway:
        """
        Patches an Istio gateway resource and returns the patched resource.
        @param name: Name of the gateway.
        @param namespace: Namespace of the gateway. Default value is "default".
        @param body: Body of the gateway. Should be a dict or Pydantic model.
        @return: The patched gateway resource in pydantic format.
        """
        return self.patch_namespaced(name, namespace, body, GATEWAY_PLURAL, V1Beta1Gateway)

    def delete_namespaced_gateway(self, name: str, namespace: str = "default") -> Optional[V1Beta1Status]:
        """
        Deletes an Istio gateway resource and returns the status of the delete operation.
        @param name: Name of the gateway.
        @param namespace: Namespace of the gateway. Default value is "default".
        @return: The status of the delete operation, as a pydantic model.
        """
        return self.delete_namespaced(name, namespace, GATEWAY_PLURAL)

    def read_namespaced_virtual_service(self, name: str, namespace: str = "default") -> Optional[V1Beta1VirtualService]:
        """
        Reads an [Istio virtual service](https://istio.io/latest/docs/reference/config/networking/virtual-service/) resource.
        Returns None if the virtual service doesn't exist.
        @param name: Name of the virtual service.
        @param namespace: Namespace of the virtual service. Default value is "default".
        @return: The virtual service resource if it exists, None otherwise.
        """
        return self.read_namespaced(name, namespace, VIRTUAL_SERVICE_PLURAL, V1Beta1VirtualService)

    def create_namespaced_virtual_service(
        self, namespace: str = "default", body: Union[dict, V1Beta1VirtualService] = None
    ) -> V1Beta1VirtualService:
        """
        Creats an Istio virtual service resource and returns the created resource.
        @param namespace: Namespace of the virtual service. Default value is "default".
        @param body: Body of the virtual service. Should be a dict or Pydantic model.
        @return: The created virtual service resource in a pydantic format.
        """
        return self.create_namespaced(namespace, body, VIRTUAL_SERVICE_PLURAL, V1Beta1VirtualService)

    def patch_namespaced_virtual_service(
        self, name: str, namespace: str = "default", body: Union[dict, V1Beta1VirtualService] = None
    ) -> V1Beta1VirtualService:
        """
        Patches an Istio virtual service resource and returns the patched resource.
        @param name: Name of the virtual service.
        @param namespace: Namespace of the virtual service. Default value is "default".
        @param body: Body of the virtual service. Should be a dict or Pydantic model.
        @return: The patched virtual service resource in pydantic format.
        """
        return self.patch_namespaced(name, namespace, body, VIRTUAL_SERVICE_PLURAL, V1Beta1VirtualService)

    def delete_namespaced_virtual_service(self, name: str, namespace: str = "default") -> Optional[V1Beta1Status]:
        """
        Deletes an Istio virtual service resource and returns the status of the delete operation.
        @param name: Name of the virtual service.
        @param namespace: Namespace of the virtual service. Default value is "default".
        @return: The status of the delete operation, as a pydantic model.
        """
        return self.delete_namespaced(name, namespace, VIRTUAL_SERVICE_PLURAL)
