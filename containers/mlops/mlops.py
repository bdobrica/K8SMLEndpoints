#!/usr/bin/env python
import logging
import time
from typing import Tuple

import kopf
from kubernetes import client as K8SClient
from kubernetes import config as K8SConfig
from kubernetes.client.rest import ApiException
from resources import Endpoint, EndpointConfig, Model
from utils import DiffLineType

K8SConfig.load_incluster_config()


@kopf.on.create("machinelearningendpoint")
def ml_endpoint_create_fn(name: str, namespace: str, spec: dict, meta: dict, **kwargs):
    """
    Create a new Machine Learning Endpoint. While there are additional custom resources (Models and EndpointConfig)
    when those are created no K8S resources are assigned to them, except for the CRD itself.

    """
    logging.info(f"Creating endpoint {name} in namespace {namespace}")
    logging.info(f"Spec: {spec}")
    logging.info(f"Meta: {meta}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        _ = Endpoint(name=name, namespace=namespace).create_handler()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.update("machinelearningendpoint")
def ml_endpoint_update_fn(name: str, namespace: str, diff: Tuple[DiffLineType], **kwargs):
    logging.info(f"Updating endpoint {name} in namespace {namespace}")
    logging.info(f"Diff: {diff}")
    logging.info(f"Meta: {meta}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        _ = Endpoint(name, namespace).update_handler(diff)
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.delete("machinelearningendpoint")
def ml_endpoint_delete_fn(name: str, namespace: str, **kwargs):
    logging.info(f"Delete endpoint {name} in namespace {namespace}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        _ = Endpoint(name, namespace).delete_handler()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.update("machinelearningendpointconfig")
def ml_endpoint_config_update_fn(name: str, namespace: str, diff: Tuple[DiffLineType], **kwargs):
    logging.info(f"Updating endpoint config {name} in namespace {namespace}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        _ = EndpointConfig(name, namespace).update_handler(diff)
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.delete("machinelearningendpointconfig")
def ml_endpoint_config_delete_fn(name: str, namespace: str, **kwargs):
    logging.info(f"Delete endpoint config {name} in namespace {namespace}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        _ = EndpointConfig(name, namespace).delete_handler()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.update("machinelearningmodel")
def ml_model_update_fn(name: str, namespace: str, diff: Tuple[DiffLineType], **kwargs):
    logging.info(f"Updating model {name} in namespace {namespace}")
    logging.info(f"Spec: {spec}")
    logging.info(f"Meta: {meta}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        _ = Model(name, namespace).update_handler(diff)
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.delete("machinelearningmodel")
def ml_model_delete_fn(name: str, namespace: str, diff: Tuple[DiffLineType], **kwargs):
    logging.info("Delete model {name} in namespace {namespace}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        _ = Model(name, namespace).delete_handler()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.daemon("machinelearningmodel")
def monitor_deployment(spec, **kwargs):
    api = K8SClient.AppsV1Api()
    deployment_name = spec["deploymentName"]
    deployment_namespace = spec["deploymentNamespace"]
    while True:
        deployment_status = api.read_namespaced_deployment_status(name=deployment_name, namespace=deployment_namespace)
        replicas = deployment_status.status.replicas
        updated_replicas = deployment_status.status.updated_replicas
        available_replicas = deployment_status.status.available_replicas
        if replicas == updated_replicas == available_replicas:
            print(f"Deployment {deployment_name} is ready!")
            return
        else:
            print(
                f"Deployment {deployment_name} is not ready yet. "
                f"Replicas: {replicas}, updated replicas: {updated_replicas}, "
                f"available replicas: {available_replicas}"
            )
        time.sleep(10)
