FROM ubuntu:18.04

RUN apt update && \
    apt install -y curl wget vim && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt update && \
    apt-get install -y nodejs && \
    npm install -g ganache-cli

COPY . /root

WORKDIR /root

RUN chmod +x /root/start.sh

ENTRYPOINT ["/root/start.sh"]