from kubernetes import config as K8SConfig
from resources import Endpoint, EndpointConfig, Model

K8SConfig.load_incluster_config()


def test_endpoint_config_create():
    model = Model(name="titanic-rfc", namespace="titanic").create(
        image="quay.io/bdobrica/ml-operator-tools:model-latest",
        artifact="https://ublo.ro/wp-content/friends/titanic.tar.gz",
    )
    endpoint_config = EndpointConfig(name="titanic-rfc", namespace="titanic").create(
        models=[
            {
                "model": "titanic-rfc",
                "weight": 42,
                "cpus": "100m",
                "memory": "100Mi",
                "instances": 2,
                "size": "1Gi",
                "path": "/mnt/nfs/models",
            }
        ]
    )
    endpoint = (
        Endpoint(name="titanic-rfc", namespace="titanic")
        .create(
            config="titanic-rfc",
            host="titanic-rfc.titanic.svc.cluster.local",
        )
        .create_handler()
    )
    endpoint_config.create_handler()
    model.create_handler()
