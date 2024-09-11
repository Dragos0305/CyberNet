FROM ubuntu:22.04

ENV TERM=linux

RUN apt-get update && apt-get dist-upgrade -y

RUN apt-get update && apt-get install -y python3-pip
RUN apt-get install -y curl

RUN mkdir -p /data/users
RUN chmod 777 /data/users
RUN chmod +t /data/users
RUN ln -s /data-ro/trip.db /data/trip.db
RUN ln -s /data-ro/users/operator /data/users/operator

RUN mkdir /tris
COPY requirements.txt /tris/requirements.txt
COPY package.json /tris/package.json

WORKDIR /tris

RUN pip3 install -r requirements.txt

RUN mkdir -p /tris/cert
COPY cert/tris.crt /tris/cert/tris.crt
COPY cert/tris.key /tris/cert/tris.key

COPY server.py /tris/server.py

CMD ["python3", "-m", "server"]
