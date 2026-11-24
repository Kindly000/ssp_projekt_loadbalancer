#!/usr/bin/env python3
import argparse
import os
import random
import socket
import threading
import time

PROFILES = {
    "video": {
        "proto": "udp",
        "ports": [5004, 8554, 19350],
        "rate_mbps": (4.0, 10.0),
        "duration_s": (4.0, 10.0),
        "packet_size": 1300,
    },
    "email": {
        "proto": "tcp",
        "ports": [10587, 10993, 10025],
        "rate_mbps": (0.5, 2.0),
        "duration_s": (0.5, 2.0),
        "packet_size": 600,
    },
    "web": {
        "proto": "tcp",
        "ports": [18080, 18443],
        "rate_mbps": (1.5, 5.0),
        "duration_s": (1.0, 3.5),
        "packet_size": 1000,
    },
}


def send_udp_flow(target_ip, dst_port, duration, rate_mbps, pkt_size, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)

    bytes_per_sec = (rate_mbps * 1000000) / 8.0
    sleep_interval = pkt_size / bytes_per_sec if bytes_per_sec > 0 else 0.01
    payload = os.urandom(pkt_size)

    end_time = time.monotonic() + duration
    next_send = time.monotonic()

    try:
        while not stop_event.is_set() and time.monotonic() < end_time:
            now = time.monotonic()
            if now >= next_send:
                try:
                    sock.sendto(payload, (target_ip, dst_port))
                except OSError:
                    pass
                next_send += sleep_interval
                if next_send < now - 0.1:
                    next_send = now
            else:
                time.sleep(min(0.005, next_send - now))
    finally:
        sock.close()


def send_tcp_flow(target_ip, dst_port, duration, rate_mbps, pkt_size, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)

    bytes_per_sec = (rate_mbps * 1000000) / 8.0
    sleep_interval = pkt_size / bytes_per_sec if bytes_per_sec > 0 else 0.01
    payload = os.urandom(pkt_size)

    end_time = time.monotonic() + duration
    next_send = time.monotonic()

    try:
        sock.connect((target_ip, dst_port))
        while not stop_event.is_set() and time.monotonic() < end_time:
            now = time.monotonic()
            if now >= next_send:
                try:
                    sock.sendall(payload)
                except OSError:
                    break
                next_send += sleep_interval
                if next_send < now - 0.1:
                    next_send = now
            else:
                time.sleep(min(0.005, next_send - now))
    except OSError:
        pass
    finally:
        sock.close()


def run_flow(target_ip, profile_name, scale_rate, stop_event):
    cfg = PROFILES[profile_name]
    dst_port = random.choice(cfg["ports"])
    rate = random.uniform(*cfg["rate_mbps"]) * scale_rate
    duration = random.uniform(*cfg["duration_s"])
    pkt_size = cfg["packet_size"]

    if cfg["proto"] == "udp":
        send_udp_flow(target_ip, dst_port, duration, rate, pkt_size, stop_event)
    else:
        send_tcp_flow(target_ip, dst_port, duration, rate, pkt_size, stop_event)


def main():
    parser = argparse.ArgumentParser(description="Generator ruchu z profilami (video, email, web)")
    parser.add_argument("--targets", required=True, help="IP celow po przecinku, np. 10.0.0.2,10.0.0.3")
    parser.add_argument("--profiles", default="video,email,web", help="Profile po przecinku: video,email,web")
    parser.add_argument("--scale-rate", type=float, default=1.0, help="Mnoznik przepustowosci (np. 0.5 aby odciazyc CPU)")
    parser.add_argument("--min-gap", type=float, default=0.25, help="Min. odstep miedzy kolejnymi przeplywami (s)")
    parser.add_argument("--max-gap", type=float, default=1.0, help="Max. odstep miedzy kolejnymi przeplywami (s)")
    args = parser.parse_args()

    targets = [ip.strip() for ip in args.targets.split(",") if ip.strip()]
    profiles = [p.strip() for p in args.profiles.split(",") if p.strip() in PROFILES]
    if not profiles:
        profiles = list(PROFILES.keys())

    stop_event = threading.Event()
    threads = []

    print("[START] Cele: {} | Profile: {} | Skala: {}x".format(targets, profiles, args.scale_rate))
    try:
        while True:
            target = random.choice(targets)
            profile = random.choice(profiles)
            gap = random.uniform(args.min_gap, args.max_gap)

            t = threading.Thread(
                target=run_flow,
                args=(target, profile, args.scale_rate, stop_event),
            )
            t.daemon = True
            t.start()
            threads = [th for th in threads if th.is_alive()]
            threads.append(t)

            time.sleep(gap)
    except KeyboardInterrupt:
        print("\n[STOP] Zatrzymywanie...")
        stop_event.set()
        for th in threads:
            th.join(timeout=1.0)


if __name__ == "__main__":
    main()