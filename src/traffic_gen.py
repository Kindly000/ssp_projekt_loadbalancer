#!/usr/bin/env python3
import argparse
import os
import random
import socket
import threading
import time


def send_flow(target_ip, duration, rate_mbps, stop_event):
    dst_port = random.randint(10000, 50000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)

    bytes_per_sec = (rate_mbps * 1000000.0) / 8.0
    packet_size = 1200
    sleep_interval = packet_size / bytes_per_sec
    payload = os.urandom(packet_size)

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


def main():
    parser = argparse.ArgumentParser(
        description="Ciągły generator zróżnicowanego ruchu UDP"
    )
    parser.add_argument(
        "--targets",
        required=True,
        help="Adresy IP celów oddzielone przecinkiem, np. 10.0.0.2,10.0.0.3",
    )
    parser.add_argument(
        "--min-rate",
        type=float,
        default=1.0,
        help="Minimalna przepustowość przepływu w Mbps",
    )
    parser.add_argument(
        "--max-rate",
        type=float,
        default=8.0,
        help="Maksymalna przepustowość przepływu w Mbps",
    )
    parser.add_argument(
        "--min-dur",
        type=float,
        default=1.0,
        help="Minimalny czas trwania przepływu (s)",
    )
    parser.add_argument(
        "--max-dur",
        type=float,
        default=5.0,
        help="Maksymalny czas trwania przepływu (s)",
    )
    parser.add_argument(
        "--min-gap",
        type=float,
        default=0.2,
        help="Minimalny odstęp między startem przepływów (s)",
    )
    parser.add_argument(
        "--max-gap",
        type=float,
        default=0.9,
        help="Maksymalny odstęp między startem przepływów (s)",
    )
    args = parser.parse_args()

    targets = [ip.strip() for ip in args.targets.split(",") if ip.strip()]
    if not targets:
        parser.error("--targets musi zawierać co najmniej jeden adres IP")
    if args.min_rate <= 0 or args.max_rate < args.min_rate:
        parser.error("Wymagane: 0 < --min-rate <= --max-rate")
    if args.min_dur <= 0 or args.max_dur < args.min_dur:
        parser.error("Wymagane: 0 < --min-dur <= --max-dur")
    if args.min_gap < 0 or args.max_gap < args.min_gap:
        parser.error("Wymagane: 0 <= --min-gap <= --max-gap")

    stop_event = threading.Event()
    threads = []

    print(
        "[START] Generator ruchu - cele {}, zakres {}-{} Mbps".format(
            targets, args.min_rate, args.max_rate
        ),
        flush=True,
    )
    try:
        while True:
            target = random.choice(targets)
            rate = random.uniform(args.min_rate, args.max_rate)
            duration = random.uniform(args.min_dur, args.max_dur)
            gap = random.uniform(args.min_gap, args.max_gap)

            thread = threading.Thread(
                target=send_flow,
                args=(target, duration, rate, stop_event),
                daemon=True,
            )
            thread.start()
            threads = [active for active in threads if active.is_alive()]
            threads.append(thread)

            time.sleep(gap)
    except KeyboardInterrupt:
        print("\n[STOP] Zatrzymywanie generatora...", flush=True)
        stop_event.set()
        for thread in threads:
            thread.join(timeout=1.0)


if __name__ == "__main__":
    main()
