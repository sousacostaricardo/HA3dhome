# Casa 3D — documentation

## What it does
Renders your home as a navigable low-poly 3D model in a sidebar panel. Device
states are read live from Home Assistant; tapping a controllable device (light,
cover, switch) calls the matching service. Climate and binary sensors are shown
read-only (climate tints the room by temperature).

## Mapping your real home
The model is driven by plan files in the add-on's config folder.

1. After first start, open the add-on's config folder:
   `/addon_configs/<repo-id>_casa3d/` (via the **File editor** or **Samba** add-on).
2. Copy `casa3d.sample.json` there and rename it to **`casa3d.json`**.
3. Edit it (see schema below), then restart the add-on.

### Multiple plans
Drop as many `*.json` plan files as you like in that folder (e.g. `casa.json`,
`garagem.json`, `escritorio.json`). Each one shows up in the **dropdown**
(top-left of the panel) and you can switch between them live — no restart
needed. The dropdown label for a plan is its `meta.name`, falling back to the
filename. Files without a `rooms` array are ignored.

### Schema
- **meta** — `name` (shown in the plan dropdown). Optional `wall`:
  `{ "color": <decimal>, "pattern": "none|tile|wood|brick|concrete" }` styles all walls.
- **rooms[]** — `id`, `name`, `poly` (list of `[x,z]` corners, metres), `tone`
  (decimal colour, e.g. `0x252d39` = `2436921`). Optional `pattern`
  (`none|tile|wood|brick|concrete`) textures the floor.
- **walls[]** — `a`/`b` are `[x,z]` endpoints; `o[]` are openings with
  `at` (0..1 along the wall), `w` (width, m), `k` (`"door"` or `"win"`).
- **furniture[]** — decorative props (no entity). `id`, `kind`, `pos` `[x,z]`,
  optional `rot` (degrees), `size` `[sx,sy,sz]` (per-axis scale), `elev`
  (height off the floor, m) and `tone` (decimal colour). `kind` is one of
  `sofa | bed | bed_double | table | sidetable | chair | chairs | bench |
  cabinet | tvstand | tv | painting | tablelamp | dininglight | curtains |
  rug | rug_round | plant | shower | sink | kitchen`.
  Optional `action` makes a prop tappable — same shape as a device's `action`,
  but include the target `entity` (the prop has none of its own), e.g.
  `{ "type": "panel", "entity": "media_player.sala" }` on a TV prop, or
  `{ "type": "toggle", "entity": "cover.sala" }` on a curtain.
- **devices[]** — `id`, `entity` (your real HA entity_id), `type`
  (`light` | `cover` | `climate` | `sensor`), `name`, `room`, `pos` `[x,z]`.
  Optional `rot` (degrees) and `size` `[sx,sy,sz]` (per-axis scale) orient and
  dimension the object. Optional `action` sets what a tap does:
  - `{ "type": "toggle" }` — toggle the entity (default for light/cover/switch/fan).
  - `{ "type": "panel" }` — open Casa 3D's own in-panel dashboard (default for climate).
  - `{ "type": "service", "domain": "...", "service": "...", "data": { } }` — call any service.
  - `{ "type": "moreinfo" }` — open Home Assistant's native more-info dialog.
  - `{ "type": "dashboard", "path": "/lovelace/clima" }` — open a Lovelace view.
  - `{ "type": "none" }` — read-only.

Coordinates are in metres; the floor lies on the X/Z plane with the model
centred near the origin. Sketch your plan on paper, read off corner coordinates,
and fill them in. You usually don't need to hand-edit any of this — use the
built-in editor (below) and hit **Guardar**.

## Editing in 3D
Click **Editar** in the bottom dock to enter edit mode:
- **+ Objeto** adds a device at the centre of the view. Select it to set its
  name, entity, type, room and click-action; **drag it on the floor** to move it;
  **Eliminar** removes it.
- **+ Móvel** adds a furniture prop. Select it to pick its type, colour,
  rotation, **dimensions** (L·A·P), **height off the floor** and a **click
  action** (with its target entity); drag to move, **Eliminar móvel** to remove. Dragging a prop over another (e.g. a lamp over a
  side table) **snaps it onto that surface**; over open floor it drops back to 0.
  Wall/ceiling props (painting, curtains, dining light) keep their set height.
- **+ Parede** adds a wall. Click any wall to edit its endpoints and its
  openings — add/remove windows & doors and set each one's position and width
  (this is how you resize a window's glass). Each wall can be deleted.
- Devices (incl. the A/C and blinds) also expose **rotation** and **dimensions**
  in their inspector, so you can size and face them to a wall.
- **Paredes** still sets the global wall colour/texture for the whole plan.
- Click a **room's floor** to change its colour, texture, **size** (Largura X /
  Profund. Z) and **position** (Centro X/Z). Tap the floor again and drag to move it.
- **Paredes** sets the colour and texture for all walls.
- **Guardar** writes everything back to the plan file that's selected in the
  dropdown (or to `casa3d.json` if you started from the built-in demo).
- **Sair** leaves edit mode (warns if you have unsaved changes).

## Controls
- Drag to orbit, pinch/scroll to zoom.
- Tap a device (or its row in the panel) to run its action (toggle, open its
  dashboard, etc. — see `action` above).
- **Recentrar** resets the camera · **Noite** switches to night lighting ·
  **Rodar** toggles auto-rotation · **Demo** forces simulated states ·
  **Editar** opens the in-3D editor.

## How it talks to Home Assistant
The add-on runs a small bridge server that uses the Supervisor proxy
(`http://supervisor/core/api`) with the auto-provided `SUPERVISOR_TOKEN`. No
token setup needed. `homeassistant_api: true` is set in `config.yaml`.

## Notes / limits (v0.1.0)
- Three.js and OrbitControls are bundled in the add-on and served locally, so
  the panel works fully offline. (Google Fonts still come from the web but fall
  back to system fonts if offline.)
- Live updates use light polling (~3s); a websocket stream can come later.
- The editor reshapes appearance and devices, not wall geometry — wall/room
  outlines are still drawn by editing the plan's `poly`/`walls` coordinates.
- Textures are generated in the browser (colour + pattern), so no image files
  are bundled and it all works offline.
