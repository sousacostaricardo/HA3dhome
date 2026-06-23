# Casa 3D — documentation

## What it does
Renders your home as a navigable low-poly 3D model in a sidebar panel. Device
states are read live from Home Assistant; tapping a controllable device (light,
cover, switch) calls the matching service. Climate and binary sensors are shown
read-only (climate tints the room by temperature).

## Mapping your real home
The model is driven by a single file: `casa3d.json`.

1. After first start, open the add-on's config folder:
   `/addon_configs/<repo-id>_casa3d/` (via the **File editor** or **Samba** add-on).
2. Copy `casa3d.sample.json` there and rename it to **`casa3d.json`**.
3. Edit it (see schema below), then restart the add-on.

### Schema
- **rooms[]** — `id`, `name`, `poly` (list of `[x,z]` corners, metres), `tone`
  (decimal colour, e.g. `0x252d39` = `2436921`).
- **walls[]** — `a`/`b` are `[x,z]` endpoints; `o[]` are openings with
  `at` (0..1 along the wall), `w` (width, m), `k` (`"door"` or `"win"`).
- **devices[]** — `id`, `entity` (your real HA entity_id), `type`
  (`light` | `cover` | `climate` | `sensor`), `name`, `room`, `pos` `[x,z]`.

Coordinates are in metres; the floor lies on the X/Z plane with the model
centred near the origin. Sketch your plan on paper, read off corner coordinates,
and fill them in.

## Controls
- Drag to orbit, pinch/scroll to zoom.
- Tap a device (or its row in the panel) to toggle it.
- **Recentrar** resets the camera · **Noite** switches to night lighting ·
  **Rodar** toggles auto-rotation · **Demo** forces simulated states.

## How it talks to Home Assistant
The add-on runs a small bridge server that uses the Supervisor proxy
(`http://supervisor/core/api`) with the auto-provided `SUPERVISOR_TOKEN`. No
token setup needed. `homeassistant_api: true` is set in `config.yaml`.

## Notes / limits (v0.1.0)
- Three.js and OrbitControls are bundled in the add-on and served locally, so
  the panel works fully offline. (Google Fonts still come from the web but fall
  back to system fonts if offline.)
- Live updates use light polling (~3s); a websocket stream can come later.
- Climate is read-only for now; tap-to-control is limited to light/cover/switch.
