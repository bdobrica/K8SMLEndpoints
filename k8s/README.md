# Kubernetes Resources

This will add the required Kubernetes resources for deploying a ML Operator. The resources are:
* A Kubernetes ServiceAccount that ties to a ClusterRole and ClusterRoleBinding to allow watching resources in any namespace.
* A few Kubernetes CustomResourceDefinitions (CRDs) that define the ML Operator resources:
    * MachineLearningModel: A machine learning model that will be deployed, consisting of a container image and a model artifact file.
    * MachineLearningEndpointConfig: A configuration for a machine learning endpoint, it can bind together multiple MachineLearningModels with different versions, weights and resources.
    * MachineLearningEndpoint: A machine learning endpoint that will be deployed and that has a MachineLearningEndpointConfig attached to it.
* A machine-learning namespace that will be used for deploying the ML Operator.
* A Kubernetes Deployment that will deploy the ML Operator.
* Example MachineLearningModel, MachineLearningEndpointConfig and MachineLearningEndpoint resources.

## How it works

* Each endpoint has an endpoint config
* Each endpoint config has a list of models with attributes (weights)
* A model can be reused in multiple endpoint configs
* An endpoint config can be reused in multiple endpoints

* When creating an endpoint with {e_name} and {namespace}:
    * Check if there's and endpoint config attached to it; if not, just stop
    * Create a gateway for the endpoint
    * Create a new instance of the endpoint config {ec_name} and {ec_version}
        * The new endpoint config will be named {ec_name}-{ec_version}
        * Store the {ec_version} in the status field of the endpoint, for later use
        * For each model from the endpoint config, create an instance with {m_name} and {m_version}
            * The new model will be named {m_name}-{m_version}
            * Store the {ec_version} in the status field of each model, for later use
            * Store the {m_versions} in the status field of the endpoint config, for later use
            * Create the storage, deployment and service for the model
        * Create a virtual service for the endpoint config
    * Add the gateway to the virtual service

## Prerequisites

* A Kubernetes cluster with at least 2 nodes.
* Istio installed on the cluster.