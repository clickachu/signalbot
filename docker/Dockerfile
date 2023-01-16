# syntax=docker/dockerfile:1
FROM ubuntu:jammy

ARG ARCH=amd64
ARG SIGNAL_CLI_VERSION=0.11.6
ARG LIBSIGNAL_CLIENT_VERSION=0.21.1

ENV ENV=/root/.profile
ENV NVM_DIR /root/.nvm

USER root
WORKDIR /root

RUN apt update && \
    apt install zip wget curl python3-pip openjdk-18-jre -y && \
    pip3 install pydbus imap_tools python-dotenv

# Install signal-cli
RUN wget https://github.com/AsamK/signal-cli/releases/download/v"${SIGNAL_CLI_VERSION}"/signal-cli-"${SIGNAL_CLI_VERSION}"-Linux.tar.gz && \
    tar xf signal-cli-"${SIGNAL_CLI_VERSION}"-Linux.tar.gz -C /opt && \
    mv /opt/signal-cli-"${SIGNAL_CLI_VERSION}" /opt/signal-cli && \
    ln -sf /opt/signal-cli/bin/signal-cli /usr/local/bin/

# Install and use libsignal-client
RUN curl -Lo libsignal_jni.so "https://gitlab.com/packaging/libsignal-client/-/jobs/artifacts/v${LIBSIGNAL_CLIENT_VERSION}/raw/libsignal-client/${ARCH}/libsignal_jni.so?job=libsignal-client-${ARCH}" && \
    zip -d /opt/signal-cli/lib/libsignal-client-*.jar libsignal_jni.so && \
    zip /opt/signal-cli/lib/libsignal-client-*.jar libsignal_jni.so

# Dbus conf
RUN wget https://raw.githubusercontent.com/AsamK/signal-cli/v"${SIGNAL_CLI_VERSION}"/data/org.asamk.Signal.conf -P /usr/share/dbus-1/system.d && \
    wget https://raw.githubusercontent.com/AsamK/signal-cli/v"${SIGNAL_CLI_VERSION}"/data/org.asamk.Signal.service -P /usr/share/dbus-1/system-services && \
    sed -i -e 's|policy user="signal-cli"|policy user="root"|' /usr/share/dbus-1/system.d/org.asamk.Signal.conf

# Install nodemon
RUN wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash && \
    echo ". $NVM_DIR/nvm.sh" >> ~/.profile && \
    . ~/.profile && \
    nvm install 18.13.0 && \
    npm install nodemon

COPY ./docker/entrypoint.sh .
COPY ./docker/daemon.sh .

RUN mkdir /run/dbus
ENTRYPOINT ["./entrypoint.sh"]
