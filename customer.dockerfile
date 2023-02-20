FROM python:3

RUN mkdir -p opt/src/customer
WORKDIR /opt/src/customer

COPY shop/customer/application.py ./application.py
COPY authentication/decorator.py ./decorator.py
COPY shop/configuration.py ./configuration.py
COPY shop/models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENTRYPOINT ["python", "./application.py"]