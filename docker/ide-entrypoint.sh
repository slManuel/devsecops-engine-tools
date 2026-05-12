#!/bin/sh
# ide-entrypoint.sh - DevSecOps Engine Tools IDE image entrypoint
#
# If ENGINE_VERSION is set (passed via the VSCode extension setting
# devsecops.general.engineToolsVersion), that specific version is installed.
# Otherwise the latest available version on PyPI is installed, ensuring the
# container never runs a stale baked-in version.

if [ -n "$ENGINE_VERSION" ]; then
    echo "[IDE] Installing devsecops-engine-tools==$ENGINE_VERSION ..."
    pip install "devsecops-engine-tools==$ENGINE_VERSION" -q \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org \
        --trusted-host pypi.python.org
else
    echo "[IDE] No ENGINE_VERSION specified, installing latest devsecops-engine-tools ..."
    pip install "devsecops-engine-tools" --upgrade -q \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org \
        --trusted-host pypi.python.org
fi

exec "$@"
