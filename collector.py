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


if __name__ == "__main__":
    import time
    while True:
        print(get_cpu())
        print(get_memory())
        print("-" * 40)
        time.sleep(1)
