#!/usr/bin/env python
import json
import logging

import kopf
from jinja2 import Environment, FileSystemLoader
from kubernetes import client as K8SClient
from kubernetes import config as K8SConfig
from kubernetes.client.rest import ApiException

templates_env = Environment(loader=FileSystemLoader("/opt/mlops/templates/"))
K8SConfig.load_incluster_config()


def get_group_and_version(api_version: str):
    api_version = api_version or ""
    if "/" in api_version:
        group, version = api_version.split("/", 2)
    else:
        group, version = "", api_version

    return group, version


def get_cr(api_version: str, namespace: str, plural: str, name: str):
    group, version = get_group_and_version(api_version)

    api_instance = K8SClient.CustomObjectsApi()
    try:
        return api_instance.get_namespaced_custom_object(group, version, namespace, plural, name)
    except ApiException:
        return None


def list_cr(api_version: str, namespace: str, plural: str):
    group, version = get_group_and_version(api_version)

    api_instance = K8SClient.CustomObjectsApi()
    try:
        return api_instance.list_namespaced_custom_object(group, version, namespace, plural)
    except ApiException:
        return None


def create_storage(namespace: str, endpoint: str, size: str):
    api_instance = K8SClient.CoreV1Api()
    pv = K8SClient.V1PersistentVolume(
        metadata=K8SClient.V1ObjectMeta(
            name=f"{endpoint}-pv",
            labels={
                "type": "local",
                "namespace": namespace,
                "component": endpoint,
            },
        ),
        spec=K8SClient.V1PersistentVolumeSpec(
            storage_class_name="manual",
            capacity={"storage": size},
            access_modes=["ReadWriteOnce"],
            host_path=K8SClient.V1HostPathVolumeSource(path=pv_path),
        ),
    )
    try:
        api_instance.create_persistent_volume(pv)
    except ApiException:
        pass
    pvc = K8SClient.V1PersistentVolumeClaim(
        metadata=K8SClient.V1ObjectMeta(
            name=f"{endpoint}-pv-claim",
            namespace=namespace,
        ),
        spec=K8SClient.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteOnce"],
            resources=K8SClient.V1ResourceRequirements(
                requests={"storage": "1Gi"},
            ),
            selector=K8SClient.V1LabelSelector(
                match_labels={
                    "namespace": namespace,
                    "component": endpoint,
                }
            ),
        ),
    )
    try:
        api_instance.create_namespaced_persistent_volume_claim(namespace, pvc)
    except ApiException:
        pass


def create_deployment(endpoint: str, instances: int, cpus: str, memory: str, image: str, env: dict):
    api_instance = K8SClient.AppsV1Api()
    deployment = K8SClient.V1Deployment(
        metadata=K8SClient.V1ObjectMeta(name=endpoint),
        spec=K8SClient.V1DeploymentSpec(
            replicas=instances,
            selector=K8SClient.V1LabelSelector(
                match_labels={"component": endpoint},
            ),
            template=K8SClient.V1PodTemplateSpec(
                metadata=K8SClient.V1ObjectMeta(labels={"component": endpoint}),
                spec=K8SClient.V1PodSpec(
                    containers=[
                        K8SClient.V1Container(
                            name=endpoint,
                            image=image,
                            resources=K8SClient.V1ResourceRequirements(
                                requests={"cpu": cpus, "memory": memory},
                                limits={"cpu": cpus, "memory": memory},
                            ),
                            env=[K8SClient.V1EnvVar(name=k, value=v) for k, v in env.items()],
                            ports=[K8SClient.V1ContainerPort(container_port=8080)],
                        )
                    ],
                    volumes=[
                        K8SClient.V1Volume(
                            name="model-volume",
                            persistent_volume_claim=K8SClient.V1PersistentVolumeClaimVolumeSource(
                                claim_name=f"{endpoint}-pv-claim",
                            ),
                        )
                    ],
                ),
            ),
        ),
    )
    try:
        api_instance.create_namespaced_deployment(namespace, deployment)
    except ApiException:
        pass


@kopf.on.create("machinelearningendpoint")
def ml_endpoint_create_fn(name: str, namespace: str, spec: dict, meta: dict, **kwargs):
    last_applied_config = meta.get("annotations", {}).get("kubectl.kubernetes.io/last-applied-configuration", "{}")
    api_version = json.loads(last_applied_config).get("apiVersion")
    endpoint_config_name = spec.get("config")
    endpoint_config = get_cr(api_version, namespace, "machinelearningendpointconfigs", endpoint_config_name)
    if not endpoint_config:
        logging.warning(f"Could not find {endpoint_config_name} in namespace {namespace}.")
        return
    endpoint_model_list = endpoint_config.get("spec", {}).get("models", [])
    for endpoint_model in endpoint_model_list:
        model = get_cr(api_version, namespace, "machinelearningmodels", endpoint_model.get("model"))
        endpoint_model.update(model.get("spec", {}))

    endpoint_template = templates_env.get_template("01-endpoint.yaml")
    endpoint_content = endpoint_template.render(namespace=namespace, models=endpoint_model_list)

    logging.info(f"template:\n{endpoint_content}")


@kopf.on.delete("machinelearningendpoint")
def ml_endpoint_delete_fn(**kwargs):
    logging.info(f"A delete handler was called with kwargs: \n{kwargs}")
