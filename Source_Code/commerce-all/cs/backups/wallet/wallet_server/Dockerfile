FROM ubuntu:22.04

ENV TERM=linux

RUN apt-get update && apt-get install -y \
    socat openssl jq

RUN mkdir /extra
COPY ascii/logo /extra
RUN touch /extra/log
RUN chown nobody:nogroup /extra/log
COPY wallet /bin/wallet
ENV MASK=20

CMD ["/usr/bin/socat", "tcp4-listen:44615,reuseaddr,fork,crnl", "exec:/bin/wallet,stderr,pty,su=nobody"]
