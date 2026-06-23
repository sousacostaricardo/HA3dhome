"""
Casa 3D — bridge server.

Serves the 3D frontend (in /www) and proxies a tiny, purpose-built API to the
Home Assistant Core API through the Supervisor:

    GET  /api/homes     -> list of every plan JSON in /config: [{"file","name"}]
    GET  /api/home      -> a plan's contents; ?file=<name.json> picks one,
                           no param falls back to casa3d.json or {"use_builtin": true}
    POST /api/home      -> ?file=<name.json>; writes the JSON body back to /config
                           (used by the in-browser editor's Save)
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
CONFIG_DIR = "/config"                   # mounted via `map: addon_config:rw`
CONFIG_FILE = os.path.join(CONFIG_DIR, "casa3d.json")
PORT = int(os.environ.get("INGRESS_PORT", "8099"))
TIMEOUT = ClientTimeout(total=10)


def list_plan_files():
    """Every readable *.json floor-plan in the config dir, newest mtime first."""
    out = []
    try:
        entries = os.listdir(CONFIG_DIR)
    except FileNotFoundError:
        return out
    for fn in entries:
        if not fn.lower().endswith(".json"):
            continue
        path = os.path.join(CONFIG_DIR, fn)
        if not os.path.isfile(path):
            continue
        name = fn[:-5]                             # filename without extension
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not isinstance(data.get("rooms"), list):
                continue                           # not a plan file, skip quietly
            meta = data.get("meta") or {}
            if meta.get("name"):
                name = str(meta["name"])
        except Exception as err:                   # malformed json -> leave it out, log it
            log.warning("plan %s could not be read: %s", fn, err)
            continue
        out.append({"file": fn, "name": name, "mtime": os.path.getmtime(path)})
    out.sort(key=lambda p: p["mtime"], reverse=True)
    for p in out:
        p.pop("mtime", None)
    return out


def _read_plan(path):
    with open(path, "r", encoding="utf-8") as f:
        return web.json_response(json.load(f))


async def get_homes(request):
    """List every plan available so the frontend can offer a dropdown."""
    return web.json_response({"homes": list_plan_files()})


async def get_home(request):
    """Return one floor-plan, or tell the frontend to use its built-in template."""
    fname = request.query.get("file")
    if fname:
        safe = os.path.basename(fname)             # no path traversal out of /config
        path = os.path.join(CONFIG_DIR, safe)
        if not safe.lower().endswith(".json") or not os.path.isfile(path):
            return web.json_response({"use_builtin": True, "error": "not found"}, status=404)
        try:
            return _read_plan(path)
        except Exception as err:
            log.warning("plan %s could not be read: %s", safe, err)
            return web.json_response({"use_builtin": True, "error": str(err)})
    # no ?file= -> legacy single-file behaviour
    try:
        return _read_plan(CONFIG_FILE)
    except FileNotFoundError:
        return web.json_response({"use_builtin": True})
    except Exception as err:                       # malformed json -> fall back, log it
        log.warning("casa3d.json could not be read: %s", err)
        return web.json_response({"use_builtin": True, "error": str(err)})


async def save_home(request):
    """Write an edited plan back to /config/<file>.json (editor Save)."""
    fname = request.query.get("file")
    if not fname:
        return web.json_response({"error": "file required"}, status=400)
    safe = os.path.basename(fname)                 # no path traversal out of /config
    if not safe.lower().endswith(".json"):
        return web.json_response({"error": "file must end in .json"}, status=400)
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "body is not valid json"}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get("rooms"), list):
        return web.json_response({"error": "a plan needs a rooms array"}, status=400)
    path = os.path.join(CONFIG_DIR, safe)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)                      # atomic swap
    except Exception as err:
        log.error("could not write %s: %s", safe, err)
        return web.json_response({"error": str(err)}, status=500)
    name = (data.get("meta") or {}).get("name") or safe[:-5]
    log.info("saved plan %s", safe)
    return web.json_response({"ok": True, "file": safe, "name": name})


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
    app.router.add_get("/api/homes", get_homes)
    app.router.add_get("/api/home", get_home)
    app.router.add_post("/api/home", save_home)
    app.router.add_get("/api/states", get_states)
    app.router.add_post("/api/service", call_service)
    app.router.add_get("/", index)
    app.router.add_get("/{path:.*}", static_or_index)
    return app


if __name__ == "__main__":
    log.info("Casa 3D bridge starting on :%s (token=%s)", PORT, "yes" if TOKEN else "no")
    web.run_app(build_app(), host="0.0.0.0", port=PORT, print=None)
