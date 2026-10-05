ARG PLAYGROUND_BASE=rti-playground@sha256:abb72066172c1b58fdb9b3592d6780025c1c22833e0b327d7a3025c2f34c5752
ARG PLAYGROUND_PLATFORM=linux/amd64
FROM --platform=${PLAYGROUND_PLATFORM} ${PLAYGROUND_BASE}

USER root

RUN rm -f /etc/apt/sources.list /etc/apt/sources.list.d/*.list /etc/apt/sources.list.d/*.sources \
    && printf '%s\n' \
        'deb [check-valid-until=no] https://snapshot.ubuntu.com/ubuntu/20261001T000000Z noble main universe' \
        'deb [check-valid-until=no] https://snapshot.ubuntu.com/ubuntu/20261001T000000Z noble-updates main universe' \
        'deb [check-valid-until=no] https://snapshot.ubuntu.com/ubuntu/20261001T000000Z noble-security main universe' \
        > /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.lock /opt/medtech-requirements.lock
RUN python3 -m venv --system-site-packages /opt/medtech-venv \
    && /opt/medtech-venv/bin/python -m pip install --no-cache-dir \
        --require-hashes --only-binary=:all: -r /opt/medtech-requirements.lock \
    && /opt/medtech-venv/bin/python -m pip check \
    && /opt/medtech-venv/bin/python -c 'import importlib.metadata as m; assert m.version("rti.connext") == "7.7.0"'

ENV NDDSHOME=/opt/rti.com/rti_connext_dds-current \
    CONNEXTDDS_ARCH=x64Linux4gcc8.5.0 \
    MEDTECH_VENV=/opt/medtech-venv

USER abc