# K8SMLEndpoints

Repository that tries to show how to implement SageMaker like endpoints in Kubernetes.

# Repo structure

* [containers](./containers/): Contains the code for the container that will be deployed in Kubernetes
    * [fluentbit](./containers/fluentbit/): Container that retrieves CPU, MEM and IO stats from the pod
    * [goreplay](./containers/goreplay/): Container that captures traffic from the pod
    * [mlops](./containers/mlops/): Container that contains the Machine Learning kubernetes operator pod
        * [resources](./containers/mlops/resources/): High level kubernetes resources abstraction
            * [istio](./containers/mlops/resources/istio/): Istio resources abstraction (VirtualService, Gateway)
            * [mlops](./containers/mlops/resources/mlops/): MLOps resources abstraction (Model, Endpoint, EndpointConfig)
        * [tests](./containers/mlops/tests/): pytest tests for the resources
        * [utils](./containers/mlops/utils/): Utilities for managing kubernetes resources (eg. versioning)
        * [mlops.py](./containers/mlops/mlops.py): Main file that contains the Machine Learning kubernetes operator
    * [model](./containers/model/): Container that contains the model serving pod, based on Titanic toy model
    * [model-init](./containers/model-init/): Container that contains the artifact downloader and unpacker pod
    * [nginx](./containers/nginx/): Container that contains the reverse proxy pod
* [k8s](./k8s/): Contains the Kubernetes manifests to deploy the container in Kubernetes
* [setup](./setup/): Contains scripts to configure Kubernetes

# Goals

* Provide a simple way to deploy ML models in Kubernetes
* Provide a simple way to swap models under the same endpoint in Kubernetes
* Provide a simple way to scale the number of replicas of an endpoint in Kubernetes
* Provide a simple way to monitor the health of an endpoint in Kubernetes
* Provide a simple way to do A/B testing of models in Kubernetes
* Provide a simple way to do canary testing of models in Kubernetes
* Provide a simple way to do blue/green testing of models in Kubernetes
