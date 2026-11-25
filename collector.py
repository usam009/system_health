import psutil

# The first call always returns 0, so call it once at startup
psutil.cpu_percent(interval=None)


def get_cpu():
    load1, load5, load15 = psutil.getloadavg()
    return {
        "percent": psutil.cpu_percent(interval=None),
        "per_core": psutil.cpu_percent(interval=None, percpu=True),
        "cores": psutil.cpu_count(),
        "load": [round(load1, 2), round(load5, 2), round(load15, 2)],
    }


def get_memory():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "percent": mem.percent,
        "used_gb": round(mem.used / 1024**3, 2),
        "total_gb": round(mem.total / 1024**3, 2),
        "swap_percent": swap.percent,
    }

import time
import platform

_prev_net = {"time": time.time(), "counters": psutil.net_io_counters(pernic=True)}
_prev_disk = {"time": time.time(), "counters": psutil.disk_io_counters()}


def get_disk():
    global _prev_disk
    now = time.time()
    io = psutil.disk_io_counters()
    dt = now - _prev_disk["time"]
    prev = _prev_disk["counters"]
    read_kbps = (io.read_bytes - prev.read_bytes) / dt / 1024 if dt > 0 else 0
    write_kbps = (io.write_bytes - prev.write_bytes) / dt / 1024 if dt > 0 else 0
    _prev_disk = {"time": now, "counters": io}

    partitions = []
    for p in psutil.disk_partitions():
        if p.fstype in ("squashfs", "tmpfs", "devtmpfs") or p.mountpoint.startswith("/snap"):
            continue
        try:
            usage = psutil.disk_usage(p.mountpoint)
        except PermissionError:
            continue
        partitions.append({
            "mount": p.mountpoint,
            "percent": usage.percent,
            "used_gb": round(usage.used / 1024**3, 1),
            "total_gb": round(usage.total / 1024**3, 1),
        })
    return {
        "partitions": partitions,
        "read_kbps": round(read_kbps, 1),
        "write_kbps": round(write_kbps, 1),
    }


def get_network():
    global _prev_net
    now = time.time()
    counters = psutil.net_io_counters(pernic=True)
    dt = now - _prev_net["time"]
    result = []
    for iface, c in counters.items():
        if iface == "lo" or iface not in _prev_net["counters"]:
            continue
        p = _prev_net["counters"][iface]
        result.append({
            "iface": iface,
            "up_kbps": round((c.bytes_sent - p.bytes_sent) / dt / 1024, 1) if dt > 0 else 0,
            "down_kbps": round((c.bytes_recv - p.bytes_recv) / dt / 1024, 1) if dt > 0 else 0,
        })
    _prev_net = {"time": now, "counters": counters}
    return result


def get_system():
    return {
        "hostname": platform.node(),
        "os": platform.freedesktop_os_release().get("PRETTY_NAME", platform.system()),
        "kernel": platform.release(),
        "uptime_seconds": int(time.time() - psutil.boot_time()),
    }
if __name__ == "__main__":
    while True:
        print(get_cpu())
        print(get_memory())
        print(get_disk())
        print(get_network())
        print(get_system())
        print("-" * 40)
        time.sleep(1)
