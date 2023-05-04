from kubernetes import config as K8SConfig
from resources.model import Model

K8SConfig.load_incluster_config()


def test_model_create():
    model = Model(name="titanic-rfc", namespace="titanic").create(
        image="quay.io/bdobrica/ml-operator-tools:model-latest",
        artifact="https://ublo.ro/wp-content/friends/titanic.tar.gz",
    )
    assert model.body.spec.image == "quay.io/bdobrica/ml-operator-tools:model-latest"
    assert model.body.spec.artifact == "https://ublo.ro/wp-content/friends/titanic.tar.gz"


def test_model_delete():
    model = Model(name="titanic-rfc", namespace="titanic").delete()
    assert model.body is None
