from kubernetes import config as K8SConfig
from resources.endpoint import Endpoint

K8SConfig.load_incluster_config()


def test_endpoint_create():
    model = Endpoint(name="titanic-rfc", namespace="titanic").create(
        config="titanic-rfc",
        host="titanic.endpoint.internal",
    )
    assert model.body.spec.config == "titanic-rfc"
    assert model.body.spec.host == "titanic.endpoint.internal"


def test_endpoint_delete():
    model = Endpoint(name="titanic-rfc", namespace="titanic").delete()
    assert model.body is None
