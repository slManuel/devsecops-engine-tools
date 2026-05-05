# =============================================================================
# DevSecOps Engine Tools — unified Dockerfile
#
# TARGETS
#   standard  Tagged by version (bancolombia/devsecops-engine-tools:<version>)
#             Built in CI for every release. Includes versioned engine-tools.
#             docker build --target standard \
#               --build-arg VERSION=x.y.z \
#               -t bancolombia/devsecops-engine-tools:x.y.z .
#
#   ide       Tagged :ide (bancolombia/devsecops-engine-tools:ide)
#             Built rarely — only when IDE config or base tools change.
#             Engine-tools version resolved at container startup via entrypoint.
#             docker build --target ide \
#               -t bancolombia/devsecops-engine-tools:ide .
#
# CUSTOM REMOTE CONFIG:
#   Both targets bake a default config from example_remote_config_local/.
#   standard — override at build time:  --build-arg REMOTE_CONFIG=./my_config
#   ide      — override at build time:  --build-arg IDE_REMOTE_CONFIG=./my_config
#            — override at runtime: mount host path via VSCode setting
#                devsecops.general.customRemoteConfigPath
# =============================================================================

# ─── Stage 1: remote_config_standard ─────────────────────────────────────────
# Builds the Python venv with a pinned devsecops-engine-tools version and
# copies the standard remote config.
FROM debian:stable-20250520-slim AS remote_config_standard

WORKDIR /app

ARG VERSION
ENV APP_VERSION=$VERSION
ARG REMOTE_CONFIG="./example_remote_config_local"
ENV REMOTE_CONFIG_PATH=$REMOTE_CONFIG

RUN apt-get update && apt-get install -y bash dos2unix

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

RUN python3 -m pip install checkov==2.3.296
RUN python3 -m pip install -i https://pypi.org/simple devsecops-engine-tools==$APP_VERSION

# ─── Stage 2: remote_config_ide ──────────────────────────────────────────────
# Builds the Python venv with only checkov baked in.
# devsecops-engine-tools is resolved at runtime by ide-entrypoint.sh.
FROM debian:stable-20250520-slim AS remote_config_ide

WORKDIR /app

ARG IDE_REMOTE_CONFIG="./example_remote_config_local"

RUN apt-get update && apt-get install -y bash dos2unix

COPY $IDE_REMOTE_CONFIG /app/ide_remote_config_build
RUN mv /app/ide_remote_config_build /app/docker_default_remote_config
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

RUN python3 -m pip install checkov==2.3.296

# ─── Stage 3: runtime_base ───────────────────────────────────────────────────
# Shared OS layer: Docker engine, Java 21, curl/wget/gnupg.
# Built once, reused as cache base for both final targets.
FROM debian:stable-20250520-slim AS runtime_base

WORKDIR /app

ENV DET_PIPELINE_NAME="" \
    DET_PATH_DIRECTORY="." \
    DET_OS="Linux" \
    DET_TEMP_DIRECTORY="/tmp" \
    DET_BRANCH_NAME="" \
    DET_SOURCE_CODE_MANAGEMENT_URI="" \
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

RUN apt-get update && \
    apt-get install -y \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/local/bin/python3

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

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    apt-transport-https \
    gnupg && \
    rm -rf /var/lib/apt/lists/*

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

COPY ./docker/rules_context_extract.py /app/rules_context_extract.py

# ─── Stage 4: standard ───────────────────────────────────────────────────────
# Default final target. Tagged by version (bancolombia/devsecops-engine-tools:<version>).
FROM runtime_base AS standard

ARG VERSION
ENV APP_VERSION=$VERSION

COPY --from=remote_config_standard /app/docker_default_remote_config /app/docker_default_remote_config
COPY --from=remote_config_standard /opt/venv /opt/venv
COPY --from=remote_config_standard /tmp/rules* /tmp/rules
COPY --from=remote_config_standard /tmp/docs* /tmp/docs
COPY --from=remote_config_standard /tmp/certificates* /tmp/certificates
COPY --from=remote_config_standard /tmp/certificates* /usr/local/share/ca-certificates
COPY --from=remote_config_standard /tmp/kics/kics-devsecops* /usr/local/bin/kics
RUN chmod +x /usr/local/bin/kics/*

COPY .envdetlocal /app/.env

ENV PATH="/opt/venv/bin:/usr/local/go/bin:/root/go/bin:/usr/local/bin/kics:$PATH"

RUN if [ -d /tmp/certificates ]; then \
    CERT_FILE=$(python3 -m certifi) && \
    cat /tmp/certificates/* >> "$CERT_FILE" && \
    echo "Certificates added to $CERT_FILE"; \
    else \
    echo "/tmp/certificates does not exist, skipping certificate addition."; \
    fi

CMD ["sh", "-c", "dockerd & while ! docker info > /dev/null 2>&1; do sleep 1; done; sh"]

# ─── Stage 5: ide ────────────────────────────────────────────────────────────
# IDE final target. Tagged :ide-vN (bancolombia/devsecops-engine-tools:ide-vN).
# Engine-tools version resolved at container startup by ide-entrypoint.sh.
FROM runtime_base AS ide

COPY --from=remote_config_ide /app/docker_default_remote_config /app/docker_default_remote_config
COPY --from=remote_config_ide /opt/venv /opt/venv
COPY --from=remote_config_ide /tmp/rules* /tmp/rules
COPY --from=remote_config_ide /tmp/docs* /tmp/docs
COPY --from=remote_config_ide /tmp/certificates* /tmp/certificates
COPY --from=remote_config_ide /tmp/certificates* /usr/local/share/ca-certificates
COPY --from=remote_config_ide /tmp/kics/kics-devsecops* /usr/local/bin/kics
RUN chmod +x /usr/local/bin/kics/*

ENV PATH="/opt/venv/bin:/usr/local/go/bin:/root/go/bin:/usr/local/bin/kics:$PATH"

RUN if [ -d /tmp/certificates ]; then \
    CERT_FILE=$(python3 -m certifi) && \
    cat /tmp/certificates/* >> "$CERT_FILE" && \
    echo "Certificates added to $CERT_FILE"; \
    else \
    echo "/tmp/certificates does not exist, skipping certificate addition."; \
    fi

# Entrypoint: installs ENGINE_VERSION at runtime if set via the IDE setting
# devsecops.general.engineToolsVersion. Falls back to latest available.
COPY ./docker/ide-entrypoint.sh /app/ide-entrypoint.sh
RUN chmod +x /app/ide-entrypoint.sh

ENTRYPOINT ["/app/ide-entrypoint.sh"]
CMD ["sh"]
