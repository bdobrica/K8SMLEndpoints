from typing import Union

from kubernetes import client as K8SClient
from kubernetes.client.rest import ApiException


class CustomResource:
    DEFAULT_GROUP = "blue.intranet"
    DEFAULT_VERSION = "v1alpha1"

    def __init__(self, name: str, plural: str, namespace: str = "default", group: str = None, version: str = None):
        self.name = name
        self.plural = plural
        self.namespace = namespace
        self.group = group or self.DEFAULT_GROUP
        self.version = version or self.DEFAULT_VERSION
        self.data = self.get_cr()
        self.metadata = {}

    def get_cr(self):
        api = K8SClient.CustomObjectsApi()
        try:
            return api.get_namespaced_custom_object(
                group=self.group, version=self.version, namespace=self.namespace, plural=self.plural, name=self.name
            )
        except ApiException:
            return {}

    def set_metadata(self, key: Union[str, dict], value: str = None):
        if isinstance(key, dict):
            self.metadata.update(key)
        else:
            self.metadata[key] = value
        return self

    def get_metadata(self, key: str = None):
        return self.metadata
