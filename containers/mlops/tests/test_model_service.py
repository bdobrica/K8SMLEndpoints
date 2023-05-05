from kubernetes import config as K8SConfig
from resources.model_service import ModelService

K8SConfig.load_incluster_config()


def test_model_service_create():
    model_service = ModelService(name="titanic-rfc", namespace="titanic").create()
    assert model_service.body.spec.selector["model"] == "titanic-rfc"
    assert model_service.body.spec.ports[0].port == 80
    assert model_service.body.spec.ports[0].target_port == 8080
    assert model_service.body.spec.ports[0].protocol == "TCP"


def test_model_service_delete():
    model_service = ModelService(name="titanic-rfc", namespace="titanic").delete()
    assert model_service.body is None
