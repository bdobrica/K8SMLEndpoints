from kubernetes import config as K8SConfig
from resources.model_deployment import ModelDeployment


def test_model_deployment_create():
    model_deployment = ModelDeployment(name="titanic-rfc", namespace="titanic").create(
        instances=2,
        artifact="https://ublo.ro/wp-content/friends/titanic.tar.gz",
        image="quay.io/bdobrica/ml-operator-tools:model-latest",
        cpus="0.1",
        memory="100Mi",
        init_image="quay.io/bdobrica/ml-operator-tools:model-init-latest",
    )

    assert model_deployment.body.spec.replicas == 2
    assert (
        model_deployment.body.spec.template.spec.containers[0].image
        == "quay.io/bdobrica/ml-operator-tools:model-latest"
    )
    assert model_deployment.body.spec.template.spec.containers[0].resources.requests["cpu"] == "0.1"
    assert model_deployment.body.spec.template.spec.containers[0].resources.requests["memory"] == "100Mi"
    assert model_deployment.body.spec.template.spec.containers[0].volume_mounts[0].name == "titanic-rfc"
    assert model_deployment.body.spec.template.spec.containers[0].volume_mounts[0].mount_path == "/opt/ml"
    assert model_deployment.body.spec.template.spec.volume_mounts[0].name == "titanic-rfc"
    assert (
        model_deployment.body.spec.template.spec.volume_mounts[0].persistent_volume_claim.claim_name
        == "titanic-rfc-pvc"
    )


def test_model_deployment_delete():
    model_deployment = ModelDeployment(name="titanic-rfc", namespace="titanic").delete()
    assert model_deployment.body is None
