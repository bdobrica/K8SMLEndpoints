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
                "model": model.body.metadata.name,
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
            config=endpoint_config.body.metadata.name,
            host="titanic-rfc.titanic.svc.cluster.local",
        )
        .create_handler()
    )
    assert endpoint.body.spec.config == "titanic-rfc"
    assert endpoint.body.spec.host == "titanic-rfc.titanic.svc.cluster.local"

    endpoint.endpoint_config.create_handler()
    assert endpoint.body.status.endpoint_config_version == endpoint_config.body.metadata.name
    assert endpoint.endpoint_config.body.status.endpoint == endpoint.body.metadata.name

    for model_ in endpoint.endpoint_config.get_models():
        print(model_.body)
        model_.create_handler()
        assert model_.body.status.endpoint == endpoint.body.metadata.name
        assert model_.body.status.endpoint_config == endpoint.endpoint_config.body.metadata.name
