FROM ubuntu:24.04

ENV TERM=linux

# SSH server
RUN apt-get update && apt-get install -y \
    openssh-server python3-pip

COPY ssh/* /etc/ssh/
RUN chmod 600 /etc/ssh/ssh_*
RUN service ssh start

RUN rm -rf /etc/update-motd.d/ /etc/legal /etc/motd /etc/issue

RUN adduser --disabled-password --shell=/bin/seismic seismic
RUN mkdir /home/seismic/.ssh
COPY ssh/client_key.pub /home/seismic/.ssh/authorized_keys

RUN chown -R root:root /home/seismic/
RUN chown seismic:seismic /home/seismic/.ssh/authorized_keys
RUN chmod 755 /home/seismic/
RUN chmod 400 /home/seismic/.ssh/authorized_keys

COPY requirements.txt /home/seismic/requirements.txt
WORKDIR /home/seismic/
RUN pip3 install -r requirements.txt --break-system-packages

COPY --chmod=755 seismic.py /bin/seismic

CMD ["/usr/sbin/sshd", "-D"]
