ARG PLAYGROUND_BASE=rti-playground:20260709a
ARG PLAYGROUND_PLATFORM=linux/amd64
FROM --platform=${PLAYGROUND_PLATFORM} ${PLAYGROUND_BASE}

USER root

RUN rm -f /etc/apt/sources.list.d/rti-deb-build.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        pkg-config \
        python3-venv \
        libgtkmm-3.0-dev \
        xvfb \
        x11vnc \
        novnc \
        websockify \
        libegl1 \
        libopengl0 \
        libxcb-cursor0 \
        libxcb-icccm4 \
        libxcb-keysyms1 \
        libxcb-shape0 \
        libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/medtech-requirements.txt
RUN python3 -m venv --system-site-packages /opt/medtech-venv \
    && /opt/medtech-venv/bin/python -m pip install --no-cache-dir \
        -r /opt/medtech-requirements.txt

ENV NDDSHOME=/opt/rti.com/rti_connext_dds-current \
    CONNEXTDDS_ARCH=x64Linux4gcc8.5.0 \
    MEDTECH_VENV=/opt/medtech-venv

USER abc