# Endpoint K8S Operator Image

## Desired Workflow

### 1. Creating an endpoint

To create an endpoint, you need to:
- create models: this will create the model storage (pv and pvc), the model deployment (with the init container) and the model service
- create endpoint this will create the weighted distribution for the model's traffic by creating a virtual service and a destination rules
- create the endpoint which is actually a gateway for the virtual service

For not wasting resources, all supporting entities will be created only after the endpoint is created.

### 2. Updating an endpoint

There are several scenarios to cover:
- updating one of the models: SageMaker doesn't allow updating the models (I think for a reason), so this will not be supported; but if it did, it will happen like this:
    - create the new model;
        - if the new model is not ready, mark the update as failure
    - update the virtual service to use the new model (use the same weight as the old one - this will work as envoy uses round robin for distribution of the traffic and both models will be serving without any interruption)
        - wait until the virtual service is ready
    - delete the old model
- updating the endpoint config:
    - updating the weights on the virtual service; no new models are created (they can be deleted if the weight is set to 0)
        - this just needs to wait on the status of the virtual service
    - swapping a model with a new one:
        - create the new model; don't do anything to the virtual service yet
        - check that the new model is ready (add a kopf daemon to check the status)
            - if the new model is not ready, mark the update as failure
        - update the virtual service to use the new model
            - wait until the virtual service is ready
        - delete the old model if necessary
- updating the endpoint
    - create the models for the new endpoint config
    - wait for them to be ready
        - if they are not ready, mark the update as failure
    - create the new virtual service and destination rules
        - wait for them to be ready
    - swap the gateway to the new virtual service
    - delete the old resources


### 3. Deleting an endpoint