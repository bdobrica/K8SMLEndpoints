# Nginx Container #

The Nginx container is responsible for exposing the model endpoint to the outside world. It is a reverse proxy that forwards the requests to the serving container. The Nginx container is a sidecar container that runs in the same pod as the serving container.