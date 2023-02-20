FROM python:3

RUN mkdir -p opt/src/daemon
WORKDIR /opt/src/daemon

COPY shop/daemon.py ./daemon.py
COPY authentication/decorator.py ./decorator.py
COPY shop/configuration.py ./configuration.py
COPY shop/models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENTRYPOINT ["python", "./daemon.py"]