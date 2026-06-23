#!/usr/bin/with-contenv bashio
export LOG_LEVEL="$(bashio::config 'log_level')"
export INGRESS_PORT="$(bashio::addon.ingress_port)"
bashio::log.info "A iniciar Casa 3D (porta ingress ${INGRESS_PORT})..."
exec python3 /server.py
