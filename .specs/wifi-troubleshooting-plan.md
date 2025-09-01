# Plan: WiFi Troubleshooting and Next Steps

## Problem

Raspberry Pi 3B was not connecting to WiFi. `wlan0` was up but always showed `Not connected`. No association attempts were visible in `wpa_supplicant` logs.

## What We Attempted

- Confirmed `wlan0` exists and is up.
- Confirmed `/etc/wpa_supplicant/wpa_supplicant.conf` exists and is readable.
- Configured `wpa_supplicant.conf` with correct SSID and PSK.
- Restarted `wpa_supplicant` and tried manual reconfiguration.
- Attempted to scan for networks (sometimes busy, sometimes not connected).
- Checked logs (`journalctl -u wpa_supplicant`) for errors or association attempts (none found).
- Tried bringing interface up/down and restarting services.
- Checked for hardware block with `rfkill` (not yet reported).
- Discovered that the system uses netplan for network configuration and there was no WiFi section for `wlan0` in `/etc/netplan/50-cloud-init.yaml`.

## Solution (FIXED)

- Edited `/etc/netplan/50-cloud-init.yaml` to add a `wifis` section for `wlan0` with the correct SSID, password, and static IP configuration.
- Applied the changes with `sudo netplan apply`.
- After rebooting, the Pi successfully connected to WiFi and was reachable at the static IP address.

## Documentation

- Record all commands tried and their outputs for future reference.
- Update this plan as new troubleshooting steps are attempted.
