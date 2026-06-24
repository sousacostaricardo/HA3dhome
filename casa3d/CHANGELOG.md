# Changelog

## 0.6.2
- **Furniture can trigger actions too.** Props now take the same click-action as
  devices (toggle / service / in-panel dashboard / more-info / Lovelace / none).
  Since a prop has no entity of its own, the action carries a target
  `entity` — e.g. tap a TV prop to open a `media_player` dashboard, or a curtain
  prop to toggle a `cover`. Set it in the móvel inspector under "Ação ao clicar".

## 0.6.1
- **Surface snapping.** Dragging a furniture prop now drops it onto the top of
  whatever furniture is directly beneath it (a table lamp lands on the side
  table, a TV on the cabinet) and snaps back to the floor over open ground —
  the elevation is set automatically. Wall/ceiling props (painting, curtains,
  dining light) are excluded and keep their manual height.

## 0.6.0
- **More props:** table lamp, LED TV, low TV cabinet, side table, dining
  pendant light, curtains, rugs (rectangular + round), and potted plants — all
  in the realistic style. New `elev` field (Altura do chão) lets a prop sit on a
  surface (e.g. a lamp on a side table) or mount at any height.
- **Editable floors:** rooms can now be **moved** (tap to select, tap again and
  drag) and **resized** (Largura X / Profund. Z, scaled from the centre) or
  repositioned numerically (Centro X/Z) right in the inspector.

## 0.5.0
- **Edit every object.** The editor now selects and edits all object classes:
  - **Walls:** click a wall to edit its endpoints (A/B x·z) and its openings —
    add/remove **windows & doors**, change each one's position and **width**
    (so you can resize the window glass). **+ Parede** adds a wall, and each wall
    can be deleted.
  - **Dimensioning:** objects and furniture now have a per-axis **size** (L·A·P)
    and **rotation**, so the A/C, blinds, and any prop can be scaled and oriented.
  - **Rooms:** can now be deleted from the inspector.
- **Realistic models.** All props and devices were redrawn with smoother
  shading and real materials (wood, fabric, brushed metal, ceramic, glass):
  - Lights are pendant lamps; the climate device is a wall-mounted **A/C split
    unit** with a status LED; covers are proper **venetian blinds** that drop slat
    by slat; sensors are ceiling domes. Windows gained frames + a centre mullion.

## 0.4.0
- **Furniture / props.** A new `furniture[]` layer adds low-poly, non-interactive
  pieces in the same flat-shaded style: sofa, single & double bed, table, chair(s),
  side cabinet, painting, shower, sink, kitchen run (cabinets + counter + fridge),
  and bench. In the editor use **+ Móvel** to add one, then pick its type, colour
  and rotation; drag to move, delete, and **Guardar** like everything else.

## 0.3.0
- **In-browser editor.** An **Editar** button turns the panel into an editor:
  - **Objects:** add (`+ Objeto`), select, drag on the floor to move, delete, and
    edit name / entity / type / room.
  - **Floors:** click a room's floor to set its **colour** and **texture**
    (tile, wood, brick, concrete — generated in-browser, no image files).
  - **Walls:** the **Paredes** button sets a colour + texture for all walls.
  - **Per-object click action:** choose what tapping an object does — `toggle`,
    call any HA `service`, open an in-panel **dashboard** (e.g. a full A/C
    thermostat with setpoint and modes), HA's native **more-info** dialog, open a
    Lovelace **dashboard** path, or nothing. Defaults are inferred from the type.
  - **Guardar** writes the changes back to the active plan's `*.json` in `/config`
    (new `POST /api/home` endpoint).

## 0.2.0
- Multiple floor-plans: the add-on now lists **every** `*.json` plan in its
  config folder, and a dropdown (top-left) lets you switch between them live.
  A plan's display name comes from its `meta.name` (falls back to the filename).
  Single-file `casa3d.json` setups keep working unchanged.

## 0.1.1
- Bundle Three.js + OrbitControls inside the add-on (served locally).
  Fixes `THREE.OrbitControls is not a constructor` and removes the CDN/internet
  dependency at runtime. The panel now works fully offline.

## 0.1.0
- First release: low-poly 3D digital twin served as an Ingress panel.
- Live state binding + two-way control for lights, covers, switches.
- Read-only climate (room tint) and binary sensors.
- Auto demo mode when no entities are mapped yet.
- Floor plan / entity mapping via /config/casa3d.json.
