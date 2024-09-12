FROM ubuntu:22.04

ENV TERM=linux

RUN apt-get update && apt-get install -y \
    socat openssl 

ADD html /html
COPY camera /bin/camera

CMD ["/usr/bin/socat", "tcp4-listen:41824,reuseaddr,fork", "exec:/bin/camera,stderr,pty,su=nobody,echo=0"] 
