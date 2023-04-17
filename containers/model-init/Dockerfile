FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y curl
RUN mkdir -p /opt/app
COPY entrypoint.sh /opt/app
RUN chmod +x /opt/app/entrypoint.sh

ENTRYPOINT [ "/opt/app/entrypoint.sh" ]
