# Changelog

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
