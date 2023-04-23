#!/usr/bin/env python
import logging

import kopf
from kubernetes import config as K8SConfig
from kubernetes.client.rest import ApiException
from resources import Endpoint, EndpointConfig, Model

K8SConfig.load_incluster_config()


@kopf.on.create("machinelearningendpoint")
def ml_endpoint_create_fn(name: str, namespace: str, spec: dict, meta: dict, **kwargs):
    logging.info(f"Creating endpoint {name} in namespace {namespace}")
    logging.info(f"Spec: {spec}")
    logging.info(f"Meta: {meta}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        endpoint = Endpoint(name, namespace).create()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.update("machinelearningendpoint")
def ml_endpoint_update_fn(name: str, namespace: str, spec: dict, meta: dict, **kwargs):
    logging.info(f"Updating endpoint {name} in namespace {namespace}")
    logging.info(f"Spec: {spec}")
    logging.info(f"Meta: {meta}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        endpoint = Endpoint(name, namespace).update()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.delete("machinelearningendpoint")
def ml_endpoint_delete_fn(name: str, namespace: str, spec: dict, meta: dict, **kwargs):
    logging.info(f"Delete endpoint {name} in namespace {namespace}")
    logging.info(f"Spec: {spec}")
    logging.info(f"Meta: {meta}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        endpoint = Endpoint(name, namespace).delete()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.update("machinelearningendpointconfig")
def ml_endpoint_config_update_fn(name: str, namespace: str, spec: dict, meta: dict, **kwargs):
    logging.info(f"Updating endpoint config {name} in namespace {namespace}")
    logging.info(f"Spec: {spec}")
    logging.info(f"Meta: {meta}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        endpoint_config = EndpointConfig(name, namespace).update()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)


@kopf.on.update("machinelearningmodel")
def ml_model_update_fn(name: str, namespace: str, spec: dict, meta: dict, **kwargs):
    logging.info(f"Updating model {name} in namespace {namespace}")
    logging.info(f"Spec: {spec}")
    logging.info(f"Meta: {meta}")
    logging.info(f"Kwargs: {kwargs}")

    try:
        model = Model(name, namespace).update()
    except ApiException as err:
        logging.error(err)
        raise kopf.PermanentError(err)
