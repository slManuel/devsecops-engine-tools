FROM debian:stable-20250520-slim AS remote_config

WORKDIR /app

ARG VERSION
ENV APP_VERSION=$VERSION
ARG REMOTE_CONFIG="./example_remote_config_local"
ENV REMOTE_CONFIG_PATH=$REMOTE_CONFIG

RUN apt-get update && apt-get install -y bash
RUN apt-get update && apt-get install -y dos2unix

COPY $REMOTE_CONFIG /app/example_remote_config_local
COPY ./docker/remoteConfigGeneration.sh /app/remoteConfigGeneration.sh
COPY ./rules* /tmp/rules
COPY ./docs* /tmp/docs
COPY ./certificates* /tmp/certificates

RUN dos2unix /app/remoteConfigGeneration.sh

RUN chmod +x /app/remoteConfigGeneration.sh
RUN /bin/bash remoteConfigGeneration.sh

RUN apt-get update && \
    apt-get install -y \
    python3-venv \
    python3-pip

RUN ln -s /usr/bin/python3 /usr/local/bin/python3 && \
    ln -s /usr/bin/pip3 /usr/local/bin/pip3

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN python3 -m pip install checkov==2.3.296
RUN python3 -m pip install -i https://pypi.org/simple devsecops-engine-tools==$APP_VERSION

FROM debian:stable-20250520-slim
WORKDIR /app

ARG VERSION
ENV APP_VERSION=$VERSION

ENV DET_PIPELINE_NAME="" \
    DET_PATH_DIRECTORY="." \
    DET_OS="Linux" \
    DET_TEMP_DIRECTORY="/tmp" \
    DET_BRANCH_NAME="" \
    DET_SOURCE_CODE_MANAGEMENT_URI="" \
    DET_BASE_COMPACT_REMOTE_CONFIG_URL="" \
    DET_ACCESS_TOKEN="" \
    DET_BUILD_EXECUTION_ID="" \
    DET_BUILD_ID="" \
    DET_BRANCH_TAG="" \
    DET_COMMIT_HASH="" \
    DET_ENVIRONMENT="" \
    DET_STAGE="Release" \
    DET_REPOSITORY_PROVIDER="" \
    DET_TARGET_BRANCH="" \
    DET_SOURCE_BRANCH="" \
    DET_ORGANIZATION="" \
    DET_PROJECT_NAME="" \
    DET_REPOSITORY=""

COPY ./docker/rules_context_extract.py /app/rules_context_extract.py
COPY --from=remote_config /app/docker_default_remote_config /app/docker_default_remote_config
COPY --from=remote_config /opt/venv /opt/venv
COPY --from=remote_config /tmp/rules* /tmp/rules
COPY --from=remote_config /tmp/docs* /tmp/docs
COPY --from=remote_config /tmp/certificate* /tmp/certificates

COPY .envdetlocal /app/.env

RUN apt-get update && \
    apt-get install -y \
    python3-venv

RUN ln -s /usr/bin/python3 /usr/local/bin/python3

ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl && \
    rm -rf /var/lib/apt/lists/*

RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    docker-ce \
    docker-ce-cli \
    npm \
    containerd.io && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    apt-transport-https \
    gnupg && \
    rm -rf /var/lib/apt/lists/*

# Add Adoptium repository
RUN wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | apt-key add - && \
    echo "deb https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list

# Install Java 21
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    temurin-21-jdk && \
    rm -rf /var/lib/apt/lists/*

RUN if [ -d /tmp/certificates ]; then \
    CERT_FILE=$(python3 -m certifi) && \
    cat /tmp/certificates/* >> "$CERT_FILE" && \
    echo "Certificates added to $CERT_FILE"; \
    else \
    echo "/tmp/certificates does not exist, skipping certificate addition."; \
    fi

CMD ["sh", "-c", "dockerd & while ! docker info > /dev/null 2>&1; do sleep 1; done; sh"]