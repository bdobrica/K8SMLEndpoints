FROM python:3.9.16-slim-bullseye

RUN mkdir -p /opt/app
COPY requirements.txt /opt/app

RUN python3 -m pip install -r /opt/app/requirements.txt

COPY predict.py /opt/app
COPY entrypoint.sh /opt/app
RUN chmod +x /opt/app/entrypoint.sh

ENTRYPOINT [ "/opt/app/entrypoint.sh" ]
