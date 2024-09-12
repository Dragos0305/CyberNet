FROM ubuntu:24.04

ENV TERM=linux

RUN apt-get update && apt-get install -y openssh-server nodejs node-sqlite3 node-log4js

COPY ssh/* /etc/ssh/
RUN chmod 600 /etc/ssh/ssh_*
RUN service ssh start

RUN adduser --disabled-password xflow
RUN mkdir /home/xflow/.ssh
COPY ssh/xflow_key.pub /home/xflow/.ssh/authorized_keys
COPY xflow.js /home/xflow/

RUN chown -R root:root /home/xflow/
RUN chown xflow:xflow /home/xflow/.ssh/authorized_keys
RUN chmod 755 /home/xflow/
RUN chmod 400 /home/xflow/.ssh/authorized_keys

CMD ["/usr/sbin/sshd", "-D"]
