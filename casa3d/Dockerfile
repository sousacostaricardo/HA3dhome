# Pinned HA base image (Alpine). Since Supervisor 2026.04 the base image is set
# here directly rather than via build.yaml / BUILD_FROM.
FROM ghcr.io/home-assistant/base:latest

# Python + aiohttp for the bridge server
RUN apk add --no-cache python3 py3-aiohttp

# App files
COPY run.sh /run.sh
COPY server.py /server.py
COPY www /www
RUN chmod a+x /run.sh

LABEL \
  io.hass.name="Casa 3D" \
  io.hass.version="0.6.0" \
  io.hass.type="app" \
  io.hass.arch="aarch64|amd64"

CMD [ "/run.sh" ]
