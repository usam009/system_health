# system_health
A Linux app that monitors the current system's health.
All files are in the current repository; please explore them and make sure you complete your assigned part of the project.
# System Health Dashboard

A lightweight, live dashboard that shows the health of an Ubuntu computer at a glance. It focuses on overall system resources (CPU, memory, disk, network), not on managing individual processes.

## Features

- **CPU**: overall usage, per-core usage, load average (1/5/15 min)
- **Memory**: RAM usage and swap usage
- **Disk**: usage per mount point, plus read/write speed
- **Network**: upload/download speed per interface
- **System info**: hostname, OS, kernel, uptime
- **Health status**: an overall badge (Healthy / Warning / Critical) with plain-language hints
- **Color thresholds**: green below 70%, amber 70-90%, red above 90%
- Updates every 2 seconds, with a "Connection lost" state if the server stops

## How it works

```
psutil  ->  collector.py  ->  Flask (app.py)  ->  /api/metrics (JSON)  ->  static/index.html
```

1. `collector.py` reads system metrics with `psutil`. CPU is sampled in a background thread, and disk/network speeds are calculated from the change between two readings.
2. `app.py` serves the metrics as JSON at `/api/metrics` and serves the dashboard page.
3. `static/index.html` polls the API every 2 seconds and draws the bars, colors, badge and hints.

## Requirements

- Ubuntu (or another Linux system)
- Python 3.9 or newer

## Setup

```bash
git clone https://github.com/usam009/system_health
cd system_health
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 app.py
```

Then open <http://127.0.0.1:5000> in your browser.

The raw data is available at <http://127.0.0.1:5000/api/metrics>.

## Testing the alerts

Generate CPU load and watch the bars and badge change:

```bash
sudo apt install stress-ng
stress-ng --cpu 16 --timeout 30s
```

Use as many `--cpu` workers as your machine has cores.

## Project structure

```
system_health/
├── app.py            # Flask server and API endpoint
├── collector.py      # Metric collection with psutil
├── health.py         # (reserved for health logic)
├── static/
│   └── index.html    # Dashboard page (HTML, CSS, JS)
├── requirements.txt
└── README.md
```

## Security note

The server binds to `127.0.0.1`, so it is only reachable from the same computer. System information can be sensitive, so don't expose it to a network without adding authentication.

## Possible improvements

- Rolling history charts (Chart.js)
- Temperature and battery metrics
- Run as a `systemd` service so it starts on boot
- Save history to SQLite, CSV export, Prometheus `/metrics` endpoint
