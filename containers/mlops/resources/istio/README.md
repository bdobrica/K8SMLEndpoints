# Istio Client #

As Istio is a Custom Resource as well, this allows using the Istio Client to interact with the Istio API. The objects are using `pydantic.BaseModel` as a base class, so you can use the `dict()` method to get a dictionary representation of the object and also initialize the object from a dictionary with the `parse_obj()` method.

## Usage ##

The below example shows how to create an Istio gateway:

```python
from mlops.istio import IstioClient

istio_client = IstioClient()
gateway_body = IstioClient.V1Beta1Gateway(
    metadata=IstioClient.V1Beta1ObjectMeta(
        name="test-gateway",
        namespace="test-namespace",
    ),
    spec=IstioClient.V1Beta1GatewaySpec(
        selector={
            "istio": "ingressgateway",
        },
        servers=[
            IstioClient.V1Beta1Server(
                hosts=[
                    "*",
                ],
                port=IstioClient.V1Beta1Port(
                    name="http",
                    number=80,
                    protocol="HTTP",
                ),
            ),
        ],
    ),
)
gateway_body: IstioClient.V1Beta1Gateway = istio_client.create_namespace("test-namespace", body=gateway_body)
```

