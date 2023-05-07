from typing import Any, Optional, Type, Union

from kubernetes import client as K8SClient
from pydantic import BaseModel
from resources.mlops.common import *
from resources.mlops.endpoint import *
from resources.mlops.endpoint_config import *
from resources.mlops.model import *


class V1Alpha1Api:
    group: str = GROUP
    version: str = VERSION

    def __init__(self, api: K8SClient.CustomObjectsApi = None) -> None:
        self.api = api or K8SClient.CustomObjectsApi()

    def read_namespaced(
        self,
        name: str,
        namespace: str = "default",
        plural: str = None,
        format: Type[BaseModel] = None,
    ) -> Optional[Union[BaseModel, dict]]:
        if name is None:
            return None
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

        print("#" * 40)
        print(result)
        print("#" * 40)

        if format:
            return format.parse_obj(result)

        return result

    def list_namespaced(
        self,
        namespace: str = "default",
        field_selector: str = None,
        label_selector: str = None,
        plural: str = None,
        format: Type[BaseModel] = None,
    ) -> Optional[List[Union[BaseModel, dict]]]:
        kwargs = {
            "group": self.group,
            "version": self.version,
            "namespace": namespace,
            "plural": plural,
            "field_selector": field_selector,
            "label_selector": label_selector,
        }

        objects = []
        while True:
            try:
                result = self.api.list_namespaced_custom_object(**kwargs)
            except K8SClient.ApiException as err:
                if err.status == 404:
                    break
                else:
                    raise

            if "continue" in result["metadata"]:
                kwargs["_continue"] = result["metadata"]["continue"]

            items = result.get("items", [])
            if not items:
                break

            if format:
                objects.extend(map(format.parse_obj, items))
            else:
                objects.extend(items)

        return objects

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

        print("")
        print("create_namespaced_custom_object", result)
        print("")

        if format:
            formatted = format.parse_obj(result)
            print("")
            print("formatted", formatted)
            print("")
            return formatted

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
    ) -> Optional[V1Alpha1Status]:
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

        return V1Alpha1Status.parse_obj(result)

    def read_namespaced_model(self, name: str, namespace: str = "default") -> Optional[V1Alpha1Model]:
        return self.read_namespaced(name, namespace, MODEL_PLURAL, V1Alpha1Model)

    def create_namespaced_model(
        self, namespace: str = "default", body: Union[dict, V1Alpha1Model] = None
    ) -> V1Alpha1Model:
        return self.create_namespaced(namespace, body, MODEL_PLURAL, V1Alpha1Model)

    def patch_namespaced_model(
        self, name: str, namespace: str = "default", body: Union[dict, V1Alpha1Model] = None
    ) -> V1Alpha1Model:
        return self.patch_namespaced(name, namespace, body, MODEL_PLURAL, V1Alpha1Model)

    def delete_namespaced_model(self, name: str, namespace: str = "default") -> Optional[V1Alpha1Status]:
        return self.delete_namespaced(name, namespace, MODEL_PLURAL)

    def read_namespaced_endpoint_config(
        self, name: str, namespace: str = "default"
    ) -> Optional[V1Alpha1EndpointConfig]:
        return self.read_namespaced(name, namespace, ENDPOINT_CONFIG_PLURAL, V1Alpha1EndpointConfig)

    def list_namespaced_endpoint_configs(
        self, namespace: str = "default", field_selector: str = None, label_selector: str = None
    ) -> List[V1Alpha1EndpointConfig]:
        return self.list_namespaced(
            namespace=namespace,
            plural=ENDPOINT_CONFIG_PLURAL,
            format=V1Alpha1EndpointConfig,
            field_selector=field_selector,
            label_selector=label_selector,
        )["items"]

    def create_namespaced_endpoint_config(
        self, namespace: str = "default", body: Union[dict, V1Alpha1EndpointConfig] = None
    ) -> V1Alpha1EndpointConfig:
        return self.create_namespaced(namespace, body, ENDPOINT_CONFIG_PLURAL, V1Alpha1EndpointConfig)

    def patch_namespaced_endpoint_config(
        self, name: str, namespace: str = "default", body: Union[dict, V1Alpha1EndpointConfig] = None
    ) -> V1Alpha1EndpointConfig:
        return self.patch_namespaced(name, namespace, body, ENDPOINT_CONFIG_PLURAL, V1Alpha1EndpointConfig)

    def delete_namespaced_endpoint_config(self, name: str, namespace: str = "default") -> Optional[V1Alpha1Status]:
        return self.delete_namespaced(name, namespace, ENDPOINT_CONFIG_PLURAL)

    def read_namespaced_endpoint(self, name: str, namespace: str = "default") -> Optional[V1Alpha1Endpoint]:
        return self.read_namespaced(name, namespace, ENDPOINT_PLURAL, V1Alpha1Endpoint)

    def list_namespaced_endpoints(
        self, namespace: str = "default", field_selector: str = None, label_selector: str = None
    ) -> List[V1Alpha1Endpoint]:
        return self.list_namespaced(
            namespace=namespace,
            plural=ENDPOINT_PLURAL,
            format=V1Alpha1Endpoint,
            field_selector=field_selector,
            label_selector=label_selector,
        )["items"]

    def create_namespaced_endpoint(
        self, namespace: str = "default", body: Union[dict, V1Alpha1Endpoint] = None
    ) -> V1Alpha1Endpoint:
        return self.create_namespaced(namespace, body, ENDPOINT_PLURAL, V1Alpha1Endpoint)

    def patch_namespaced_endpoint(
        self, name: str, namespace: str = "default", body: Union[dict, V1Alpha1Endpoint] = None
    ) -> V1Alpha1Endpoint:
        return self.patch_namespaced(name, namespace, body, ENDPOINT_PLURAL, V1Alpha1Endpoint)

    def delete_namespaced_endpoint(self, name: str, namespace: str = "default") -> Optional[V1Alpha1Status]:
        return self.delete_namespaced(name, namespace, ENDPOINT_PLURAL)
