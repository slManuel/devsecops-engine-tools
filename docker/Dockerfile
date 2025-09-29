FROM #{ubuntu_24.04}# AS remote_config


WORKDIR /app

ARG VERSION
ENV APP_VERSION=$VERSION
ARG REMOTE_CONFIG="./example_remote_config_local"
ENV REMOTE_CONFIG_PATH=$REMOTE_CONFIG


ARG DEFECT_DOJO_SECRET
ENV DEFECT_DOJO_SECRET=$DEFECT_DOJO_SECRET

RUN apt-get update && apt-get install -y bash
RUN apt-get update && apt-get install -y dos2unix

COPY $REMOTE_CONFIG /app/example_remote_config_local
RUN mv /app/example_remote_config_local /app/docker_default_remote_config
COPY ./rules* /tmp/rules
COPY ./docs* /tmp/docs
COPY ./certificates* /tmp/certificates
COPY ./kics_binary* /tmp/kics

RUN apt-get update && \
    apt-get install -y \
    python3-venv \
    python3-pip

RUN ln -s /usr/bin/python3 /usr/local/bin/python3 && \
    ln -s /usr/bin/pip3 /usr/local/bin/pip3

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN python3 -m pip install checkov==3.2.311
RUN python3 -m pip install -i https://pypi.org/simple devsecops-engine-tools==$APP_VERSION

ENV PATH="/opt/venv/bin:/usr/local/go/bin:$PATH"

FROM #{ubuntu_24.04}#
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
COPY --from=remote_config /tmp/certificates* /tmp/certificates
COPY --from=remote_config /tmp/certificates* /usr/local/share/ca-certificates
COPY --from=remote_config /tmp/kics/kics-devsecops* /usr/local/bin/kics
RUN chmod +x /usr/local/bin/kics/*

COPY .envdetlocal /app/.env

RUN apt-get update && \
    apt-get install -y \
    python3-venv

RUN ln -s /usr/bin/python3 /usr/local/bin/python3

ENV PATH="/opt/venv/bin:/usr/local/go/bin:/root/go/bin:/usr/local/bin/kics:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl && \
    rm -rf /var/lib/apt/lists/*

RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" \
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

# Crear carpeta de keyrings y descargar la clave
RUN install -m 0755 -d /etc/apt/keyrings && \
    wget -O /etc/apt/keyrings/adoptium.asc https://packages.adoptium.net/artifactory/api/gpg/key/public && \
    chmod a+r /etc/apt/keyrings/adoptium.asc && \
    echo "deb [signed-by=/etc/apt/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb $(. /etc/os-release && echo \"$VERSION_CODENAME\") main" \
    | tee /etc/apt/sources.list.d/adoptium.list
    
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