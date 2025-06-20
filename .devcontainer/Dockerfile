ARG UBUNTU_VERSION=22.04

FROM mcr.microsoft.com/devcontainers/base:ubuntu-${UBUNTU_VERSION}

ARG UBUNTU_VERSION
ARG OIDC_AGENT_VERSION=5.1.0-1

# Install oidc-agent
RUN apt-get update && \
    apt-get install -y curl
RUN curl repo.data.kit.edu/repo-data-kit-edu-key.gpg \
    | gpg --dearmor \
    > /etc/apt/trusted.gpg.d/kitrepo-archive.gpg && \
    echo "deb [signed-by=/etc/apt/trusted.gpg.d/kitrepo-archive.gpg] https://repo.data.kit.edu//ubuntu/${UBUNTU_VERSION} ./" \
    >> /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y oidc-agent=${OIDC_AGENT_VERSION} && \
    apt-get clean

# Set up oidc-agent environment
RUN oidc-agent > ~/.oidc-agent.env
RUN echo "test -e ~/.oidc-agent.env && . ~/.oidc-agent.env" >> ~/.bashrc
