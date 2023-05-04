from mlops.resources.model import Model


def test_model_create():
    model = Model(name="titanic-rfc", namespace="titanic").create(
        image="quay.io/bdobrica/ml-operator-tools:model-latest",
        artifact="https://ublo.ro/wp-content/friends/titanic.tar.gz",
    )
    assert model.body.spec.image == "quay.io/bdobrica/ml-operator-tools:model-latest"
    assert model.body.spec.artifact == "https://ublo.ro/wp-content/friends/titanic.tar.gz"
