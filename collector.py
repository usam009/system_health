import platform
import threading
import time

import psutil

# ---------- CPU (sampled in one background thread) ----------
_cpu_cache = {"percent": 0.0, "per_core": [0.0] * psutil.cpu_count()}


def _cpu_sampler():
    while True:
        per_core = psutil.cpu_percent(interval=1, percpu=True)
        _cpu_cache["per_core"] = per_core
        _cpu_cache["percent"] = round(sum(per_core) / len(per_core), 1)


threading.Thread(target=_cpu_sampler, daemon=True).start()


def get_cpu():
    load1, load5, load15 = psutil.getloadavg()
    return {
        "percent": _cpu_cache["percent"],
        "per_core": _cpu_cache["per_core"],
        "cores": psutil.cpu_count(),
        "load": [round(load1, 2), round(load5, 2), round(load15, 2)],
    }


# ---------- Memory ----------
def get_memory():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "percent": mem.percent,
        "used_gb": round(mem.used / 1024**3, 2),
        "total_gb": round(mem.total / 1024**3, 2),
        "swap_percent": swap.percent,
    }


# ---------- Disk ----------
_lock = threading.Lock()
_prev_disk = {"time": time.time(), "counters": psutil.disk_io_counters()}
_prev_net = {"time": time.time(), "counters": psutil.net_io_counters(pernic=True)}


def get_disk():
    global _prev_disk
    read_kbps = write_kbps = 0.0
    io = psutil.disk_io_counters()
    now = time.time()
    with _lock:
        prev = _prev_disk["counters"]
        dt = now - _prev_disk["time"]
        if io and prev and dt > 0:
            read_kbps = (io.read_bytes - prev.read_bytes) / dt / 1024
            write_kbps = (io.write_bytes - prev.write_bytes) / dt / 1024
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


# ---------- Network ----------
def get_network():
    global _prev_net
    now = time.time()
    counters = psutil.net_io_counters(pernic=True)
    result = []
    with _lock:
        dt = now - _prev_net["time"]
        for iface, c in counters.items():
            if iface == "lo" or iface not in _prev_net["counters"] or dt <= 0:
                continue
            p = _prev_net["counters"][iface]
            result.append({
                "iface": iface,
                "up_kbps": round((c.bytes_sent - p.bytes_sent) / dt / 1024, 1),
                "down_kbps": round((c.bytes_recv - p.bytes_recv) / dt / 1024, 1),
            })
        _prev_net = {"time": now, "counters": counters}
    return result


# ---------- System info ----------
def get_system():
    try:
        os_name = platform.freedesktop_os_release().get("PRETTY_NAME", platform.system())
    except OSError:
        os_name = platform.system()
    return {
        "hostname": platform.node(),
        "os": os_name,
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
