#!/usr/bin/env python
import logging

import kopf
from kubernetes import config as K8SConfig
from kubernetes.client.rest import ApiException
from resources import Endpoint

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
