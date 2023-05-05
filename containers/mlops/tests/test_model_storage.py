from kubernetes import config as K8SConfig
from resources.model_storage import ModelStorage

K8SConfig.load_incluster_config()


def test_model_storage_create():
    model_storage = ModelStorage(name="titanic-rfc", namespace="titanic").create(
        size="1Gi",
        path="/mnt/nfs/models",
    )
    assert model_storage.pv.spec.storage_class_name == "manual"
    assert model_storage.pv.spec.capacity["storage"] == "1Gi"
    assert model_storage.pv.spec.access_modes[0] == "ReadWriteOnce"
    assert model_storage.pv.spec.host_path.path == "/mnt/nfs/models/titanic-rfc"
    assert model_storage.pvc.spec.access_modes[0] == "ReadWriteOnce"
    assert model_storage.pvc.spec.resources.requests["storage"] == "1Gi"
    assert model_storage.pvc.spec.selector.match_labels["type"] == "local"
    assert model_storage.pvc.spec.selector.match_labels["namespace"] == "titanic"
    assert model_storage.pvc.spec.selector.match_labels["model"] == "titanic-rfc"


def test_model_storage_delete():
    model_storage = ModelStorage(name="titanic-rfc", namespace="titanic").delete()
    assert model_storage.pv is None
    assert model_storage.pvc is None
