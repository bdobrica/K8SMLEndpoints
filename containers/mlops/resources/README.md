# MLOps Resources #

This package contains the custom resources used by the MLOps framework.

The following objects are available:

- `MLOpsClient.V1Alpha1Model`: A model object mirroring the `Model` CRD. It can be used to create, update and delete models which link a container image to a model artifact. Its dependant resources are:
    - a persistent volume which is used to store the model artifact
    - a persistent volume claim which is used to claim the persistent volume
    - a deployment which is used to deploy the container image. The pod templates contain:
        - an init container which is used to download the model artifact and unpack it to the persistent volume
        - a container which is used to serve the model artifact from the persistent volume
        - a sidecar container which is used to expose the monitoring endpoint via nginx
        - a sidecar containing [fluentbit](https://fluentbit.io/) to collect cpu usage, memory usage and latency metrics
        - a sidecar containing [gor](https://github.com/buger/goreplay) to capture data
    - a service which is used to expose the deployment
- `MLOpsClient.V1Alpha1EndpointConfig`: An endpoint config object mirroring the `EndpointConfig` CRD. It can be used to create, update and delete endpoint configs which link multiple models behind a single endpoint, allowing weight-based routing between the models. The endpoint config contains among the models and their weights also their instance details like the number of replicas and the compute resources. Its dependant resources are:
    - an Istio virtual service which is used to route traffic to the models
- `MLOpsClient.V1Alpha1Endpoint`: An endpoint object mirroring the `Endpoint` CRD. It can be used to create, update and delete endpoints which link an endpoint config to a Istio gateway. The endpoint contains the URL of the endpoint and the URL of the monitoring endpoint.
    - an Istio gateway which is used to expose the endpoint

Each resource has a set of `create`, `update`, `delete` methods which can be used to interact with the Kubernetes API. There are also `create_handler`, `update_handler` and `delete_handler` which can be used to interact with dependant resources (e.g. creating a model is actually deploying a persistent volume, a persistent volume claim, a deployment and a service).