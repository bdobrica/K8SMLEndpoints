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

## Prerequisites

* A Kubernetes cluster with at least 2 nodes.
* Istio installed on the cluster.