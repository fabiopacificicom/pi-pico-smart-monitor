# Deployment Strategy for pi-pico-smart-monitor

This document describes a pragmatic, safe, and auditable deployment strategy for the project components:
- Raspberry Pi (central server / Flask API)
- Pico-W (Wi‑Fi pump controller with moisture sensor)
- Pico (non‑WiFi devices connected via USB)

## Goals
- Reliable, automated updates for devices.
- Safe: atomic updates and easy rollback on failure.
- Auditable: versioned artifacts and device reporting.
- Low operational complexity for single-device and small-fleet setups.

## Overview
1. CI builds and publishes versioned artifacts (source bundles, UF2 for Pico, checksums).
2. Raspberry Pi performs either pull-based updates (recommended) or accepts pushed artifacts from CI.
3. Pico‑W performs secure OTA pull from a trusted artifact endpoint and replaces its application atomically.
4. Non‑WiFi Pico devices are updated by the Pi over USB (mount/UF2 copy or serial deploy).
5. Devices report deploy and health status back to the Pi for monitoring.

## Phases

### Phase 1 — Minimal viable deploy (manual triggers)
- CI publishes artifacts to GitHub Releases or a simple HTTP server.
- Pi: implement a `deploy.sh` that downloads artifact, backs up current app, restarts service, and runs health checks.
- Pico‑W: add a small periodic puller in `boot.py`/`main.py` to check a `meta.json` endpoint and download a new `main.py` when available. Use placeholder `TELEMETRY_URL` / `ARTIFACT_URL` variables.

### Phase 2 — Automated / scheduled rollout
- Use a webhook or systemd timer on the Pi to trigger pulls when new artifacts appear.
- Add staged rollout flags (e.g., `rollout=canary|all`) to CI metadata so devices can choose whether to apply immediately.

### Phase 3 — Fleet management and secure signing
- Add artifact signing (HMAC or asymmetric) and verification on Pico‑W.
- Add device heartbeat and deploy logs to a central dashboard.

## CI / Artifact strategy
- Build artifacts on CI when `main` is updated and on new tags:
  - Pi artifact: source tarball (or single-file package) with version metadata and checksum.
  - Pico‑W artifact: plain `main.py` or a ZIP/UF2 depending on update method.
  - Non‑WiFi Pico: UF2 images if full firmware rebuild needed, otherwise source files for copying.
- Publish artifacts to GitHub Releases, S3, or a static HTTP directory. Publish a `meta.json` next to each artifact containing:
  - `version`, `artifact_url`, `sha256`, `signature`, `rollout` tag, `created_at`.

## Raspberry Pi deployment (recommended: pull-based)
- Components:
  - `deploy.sh` — download artifact, verify checksum, backup current app directory, install, run tests, restart systemd service.
  - `systemd` service for the Flask app and a `systemd` timer or a webhook listener that runs `deploy.sh` when a new release is available.

### Example `deploy.sh` (concept)
```bash
# /usr/local/bin/deploy.sh
set -e
WORKDIR=/opt/pi-pico-smart-monitor
BACKUP=/opt/backups/pi-pico-smart-monitor-$(date -u +%Y%m%dT%H%M%SZ)
ARTIFACT_URL="$1"
SHA256_EXPECTED="$2"

mkdir -p "$BACKUP"
cp -a "$WORKDIR"/* "$BACKUP"/
curl -fsSL "$ARTIFACT_URL" -o /tmp/artifact.tar.gz
echo "$SHA256_EXPECTED  /tmp/artifact.tar.gz" | sha256sum -c -
tar -xzf /tmp/artifact.tar.gz -C "$WORKDIR"
# optional: install deps, run smoke tests
systemctl restart pi-sensors.service
# health check
if ! curl -fsS http://localhost:5000/healthz; then
  echo "Health check failed, rolling back"
  rm -rf "$WORKDIR"/*
  cp -a "$BACKUP"/* "$WORKDIR"/
  systemctl restart pi-sensors.service
  exit 1
fi
```

## Pico‑W OTA pattern (safe, minimal)
- Requirements on device: `urequests` available, `json`, and ability to write to `/flash` atomically.
- Device checks `meta.json` periodically. When it finds a newer `version`, it:
  1. downloads artifact to `/flash/app.tmp` (binary or text),
  2. verifies SHA256 (and signature if available),
  3. moves temp file to `/flash/main.py` (or swaps symlink),
  4. posts deploy status to the Pi (or central server),
  5. calls `machine.reset()`.

### Pico‑W pseudo-code (concept)
```python
def ota_update(meta_url, artifact_url, expected_sha):
    # download to /flash/app.tmp
    # verify sha256
    # write to /flash/main.py.tmp then os.rename
    # post status, reset
```

Notes on atomicity: always write to a temp file and rename. Avoid partial overwrite of `main.py`.

## Non‑WiFi Pico updates via Pi
- Pi detects Pico USB insertion (udev rule or polling `/dev/ttyACM*`).
- If Pico mounts as mass storage (UF2 bootloader), Pi copies the UF2 file into the mountpoint.
- Alternatively, use `rshell`/`ampy`/`mpremote` to push files over serial programmatically.

## Security and integrity
- Always publish SHA256 and sign artifacts in CI. Verify on-device before replacing the running app.
- Use HTTPS for artifact delivery.
- Consider device-level authentication (API token) when devices post status to Pi.

## Health checks, rollback, and observability
- Pi deploy script runs a health check after restart; rollback to backup on failure.
- Pico‑W should report boot success and regular heartbeats (POST /deploy/status).
- Maintain a small deploy log store on the Pi with: device id, version, timestamp, result, and last seen.

## Staged rollout and canary testing
- Use `meta.json` rollout fields to mark releases as `canary` or `stable`.
- Pico‑W devices can be configured to only apply `canary` if their `device_type` matches.

## Developer workflow (quick)
1. Develop and test locally on device.
2. Tag release `vX.Y.Z` and push to GitHub.
3. CI builds artifacts and publishes metadata (meta.json + checksum + signature).
4. Pi webhook or timer downloads artifact and runs `deploy.sh`.
5. Pico‑W devices poll `meta.json` and apply updates if `rollout` allows.

## Rollout checklist (pre-deploy)
- Confirm artifact builds and checksums in CI.
- Smoke-test artifact in a staging environment.
- Prepare rollback plan and reachable backup on Pi.

## Post-deploy verification
- Pi: check service health endpoint, logs, and API response.
- Pico‑W: check heartbeat and reported firmware version via telemetry.

## Appendices
- Appendix A: sample `systemd` unit (Pi)
- Appendix B: sample GitHub Actions workflow (build + release)
- Appendix C: Pico‑W OTA code snippet (full example)

## References
- Keep this doc updated and move any code snippets to `./.specs/deployment/snippets/` for easier testing.

---
Drafted: 2026-01-02
