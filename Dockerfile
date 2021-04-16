FROM golang:1.16.3-buster AS stratum-ping-builder

ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN mkdir -p /home/docker; \
    cd /home/docker; \
    git clone https://github.com/2miners/stratum-ping --depth 1; \
    cd stratum-ping; \
    go build main.go;

FROM debian:latest

ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

COPY --from=stratum-ping-builder /home/docker/stratum-ping/main /home/docker/stratum-ping
COPY test.py /home/docker/test.py
COPY requirements.txt /home/docker/ 
RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean all; \
    cd /home/docker; \
    pip3 install --upgrade pip; \
    pip3 install -r requirements.txt; \
    chmod +x /home/docker/test.py ; \
    apt-get update && apt-get install -y curl coreutils jq && apt-get clean all;

WORKDIR /home/docker

ENTRYPOINT ["python3","/home/docker/test.py"]