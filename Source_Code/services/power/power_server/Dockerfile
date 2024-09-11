FROM ubuntu:22.04

ENV TERM=linux

RUN apt-get update && apt-get install -y socat openssl

COPY power /bin/power

CMD ["/usr/bin/socat", "tcp4-listen:46630,reuseaddr,fork", "exec:/bin/power,su=nobody"]
