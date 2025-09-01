# Plan: Robust Flask Server Service (systemd)

TODO: @copilot

## Goal

Implement a robust, production-grade systemd service to start and manage the Flask server on the Raspberry Pi.

## Steps

1. **Create a systemd service file**
   - Path: `/etc/systemd/system/pi-server.service`
   - Configure `User`, `WorkingDirectory`, and `ExecStart` for your environment.
2. **Service configuration**
   - Ensure `Restart=always` for auto-restart on failure.
   - Set `After=network.target` to ensure network is up before starting.
3. **Enable and start the service**
   - `sudo systemctl daemon-reload`
   - `sudo systemctl enable pi-server`
   - `sudo systemctl start pi-server`
4. **Logging and troubleshooting**
   - Use `journalctl -u pi-server` to view logs.
   - Adjust logging as needed (e.g., output to a file).
5. **Testing**
   - Reboot and verify the service starts automatically.
   - Confirm Flask server is accessible on boot.

## Notes

- This approach is more robust than cron: handles restarts, logs, and dependencies.
- Can be extended to manage environment variables, virtualenv, etc.
