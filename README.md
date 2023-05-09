# K8SMLEndpoints

Repository that tries to show how to implement SageMaker like endpoints in Kubernetes.

# Repo structure

* `container`: Contains the code for the container that will be deployed in Kubernetes
    * `fluentbit`: Container that retrieves CPU, MEM and IO stats from the pod
    * `goreplay`: Container that captures traffic from the pod
    * `mlops`: Container that contains the Machine Learning kubernetes operator pod
        * `resources`: High level kubernetes resources abstraction
        * `tests`: pytest tests for the resources
        * `utils`: Utilities for managing kubernetes resources (eg. versioning)
        * `mlops.py`: Main file that contains the Machine Learning kubernetes operator
    * `model`: Container that contains the model serving pod, based on Titanic toy model
    * `model-init`: Container that contains the artifact downloader and unpacker pod
    * `nginx`: Container that contains the reverse proxy pod
* `k8s`: Contains the Kubernetes manifests to deploy the container in Kubernetes
* `server`: Contains scripts to configure Kubernetes

# Goals

* Provide a simple way to deploy ML models in Kubernetes
* Provide a simple way to swap models under the same endpoint in Kubernetes
* Provide a simple way to scale the number of replicas of an endpoint in Kubernetes
* Provide a simple way to monitor the health of an endpoint in Kubernetes
* Provide a simple way to do A/B testing of models in Kubernetes
* Provide a simple way to do canary testing of models in Kubernetes
* Provide a simple way to do blue/green testing of models in Kubernetes
