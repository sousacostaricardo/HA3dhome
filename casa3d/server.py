"""
Casa 3D — bridge server.

Serves the 3D frontend (in /www) and proxies a tiny, purpose-built API to the
Home Assistant Core API through the Supervisor:

    GET  /api/home      -> contents of /config/casa3d.json, or {"use_builtin": true}
    GET  /api/states    -> proxied HA states
    POST /api/service   -> {"domain","service","entity_id"[, "data"]} -> HA service call

Auth is handled with the SUPERVISOR_TOKEN that the Supervisor injects into the
add-on container, so the user never has to create or paste a token.
"""
import os
import json
import logging

from aiohttp import web, ClientSession, ClientTimeout

LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("casa3d")

TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
CORE = "http://supervisor/core/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

WWW = "/www"
CONFIG_FILE = "/config/casa3d.json"     # mounted via `map: addon_config:rw`
PORT = int(os.environ.get("INGRESS_PORT", "8099"))
TIMEOUT = ClientTimeout(total=10)


async def get_home(request):
    """Return the user's floor-plan, or tell the frontend to use its built-in template."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return web.json_response(json.load(f))
    except FileNotFoundError:
        return web.json_response({"use_builtin": True})
    except Exception as err:                       # malformed json -> fall back, log it
        log.warning("casa3d.json could not be read: %s", err)
        return web.json_response({"use_builtin": True, "error": str(err)})


async def get_states(request):
    if not TOKEN:
        return web.json_response({"error": "no supervisor token"}, status=503)
    try:
        async with ClientSession(timeout=TIMEOUT) as s:
            async with s.get(f"{CORE}/states", headers=HEADERS) as r:
                data = await r.json()
        return web.json_response(data)
    except Exception as err:
        log.error("states proxy failed: %s", err)
        return web.json_response({"error": str(err)}, status=502)


async def call_service(request):
    if not TOKEN:
        return web.json_response({"error": "no supervisor token"}, status=503)
    try:
        body = await request.json()
        domain = body["domain"]
        service = body["service"]
        payload = {}
        if body.get("entity_id"):
            payload["entity_id"] = body["entity_id"]
        for k, v in (body.get("data") or {}).items():
            payload[k] = v
        url = f"{CORE}/services/{domain}/{service}"
        async with ClientSession(timeout=TIMEOUT) as s:
            async with s.post(url, headers=HEADERS, json=payload) as r:
                text = await r.text()
                return web.Response(status=r.status, text=text,
                                    content_type="application/json")
    except Exception as err:
        log.error("service proxy failed: %s", err)
        return web.json_response({"error": str(err)}, status=502)


async def index(request):
    return web.FileResponse(os.path.join(WWW, "index.html"))


async def static_or_index(request):
    rel = request.match_info.get("path", "")
    candidate = os.path.normpath(os.path.join(WWW, rel))
    if candidate.startswith(WWW) and os.path.isfile(candidate):
        return web.FileResponse(candidate)
    return web.FileResponse(os.path.join(WWW, "index.html"))


def build_app():
    app = web.Application()
    app.router.add_get("/api/home", get_home)
    app.router.add_get("/api/states", get_states)
    app.router.add_post("/api/service", call_service)
    app.router.add_get("/", index)
    app.router.add_get("/{path:.*}", static_or_index)
    return app


if __name__ == "__main__":
    log.info("Casa 3D bridge starting on :%s (token=%s)", PORT, "yes" if TOKEN else "no")
    web.run_app(build_app(), host="0.0.0.0", port=PORT, print=None)
