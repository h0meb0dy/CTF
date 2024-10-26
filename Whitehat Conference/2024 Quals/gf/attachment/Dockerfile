FROM ubuntu:22.04@sha256:a6d2b38300ce017add71440577d5b0a90460d0e57fd7aec21dd0d1b0761bbfb2

RUN apt update
RUN apt-get install -y socat xinetd
ENV TERM=linux

RUN useradd -ms /bin/bash pwn

WORKDIR /home/pwn

ADD ./share/gf .

RUN echo "#!/bin/bash\ntimeout 60 /home/pwn/haha" \
        > /home/pwn/run.sh
RUN chown -R root:pwn /home/pwn
RUN chmod -R 750 /home/pwn

ADD ./pwn.xinetd /etc/xinetd.d/pwn

CMD ["/usr/sbin/xinetd", "-dontfork"]
