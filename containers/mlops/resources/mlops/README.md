# Custom Resources Client #

As Custom Resources are just Kubernetes objects, you can use something similar to the Kubernetes Client to interact with them. The objects are using `pydantic.BaseModel` as a base class, so you can use the `dict()` method to get a dictionary representation of the object and also initialize the object from a dictionary with the `parse_obj()` method.