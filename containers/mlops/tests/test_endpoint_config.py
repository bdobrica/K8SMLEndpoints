from kubernetes import config as K8SConfig
from resources.endpoint_config import EndpointConfig

K8SConfig.load_incluster_config()


def test_endpoint_config():
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
            },
        ]
    )
    assert endpoint_config.body.spec.models[0].model == "titanic-rfc"
    assert endpoint_config.body.spec.models[0].weight == 42
    assert endpoint_config.body.spec.models[0].cpus == "100m"
    assert endpoint_config.body.spec.models[0].memory == "100Mi"
    assert endpoint_config.body.spec.models[0].instances == 2
    assert endpoint_config.body.spec.models[0].size == "1Gi"
    assert endpoint_config.body.spec.models[0].path == "/mnt/nfs/models"


def test_endpoint_config_delete():
    endpoint_config = EndpointConfig(name="titanic-rfc", namespace="titanic").delete()
    assert endpoint_config.body is None
