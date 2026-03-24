import socket
import time
import statistics
import struct

# ── Configuration ─────────────────────────────────────────────────
REFLECTOR_IP   = "192.168.100.165"  # replace with Node B's IP address
PORT           = 5005
PACKETS        = 200
PAYLOAD_SIZES  = [20, 50, 100, 150, 240]
TIMEOUT_S      = 5.0
INTER_PACKET_S = 0.1              # 100ms between packets — Wi-Fi has no duty cycle

# ── Main ──────────────────────────────────────────────────────────
def run_test(sock, payload_size):
    print(f"# --- payload_bytes={payload_size} packets={PACKETS}")
    
    results = []
    ok_count = 0

    for seq in range(PACKETS):
        # Build payload: first 2 bytes = sequence number, rest = padding
        payload = struct.pack(">H", seq) + bytes([seq % 256] * (payload_size - 2))

        t_start = time.perf_counter()

        try:
            sock.sendto(payload, (REFLECTOR_IP, PORT))
            data, _ = sock.recvfrom(1024)
            t_end = time.perf_counter()

            rtt_ms = (t_end - t_start) * 1000.0

            # Verify sequence number in echo
            rxseq = struct.unpack(">H", data[:2])[0]

            if rxseq == seq:
                ok_count += 1
                results.append(rtt_ms)
                print(f"{seq},{payload_size},{rtt_ms:.3f},OK")
            else:
                print(f"{seq},{payload_size},0.000,SEQ_ERROR")

        except socket.timeout:
            print(f"{seq},{payload_size},0.000,LOSS")

        time.sleep(INTER_PACKET_S)

    # Calculate statistics
    pdr = ok_count / PACKETS * 100.0

    if results:
        mean_rtt  = statistics.mean(results)
        sd_rtt    = statistics.stdev(results) if len(results) > 1 else 0
        p95_rtt   = sorted(results)[int(len(results) * 0.95)]
        p99_rtt   = sorted(results)[int(len(results) * 0.99)]
        jitter    = sd_rtt
    else:
        mean_rtt = sd_rtt = p95_rtt = p99_rtt = jitter = 0

    print(f"# SUMMARY payload_bytes={payload_size}")
    print(f"#   sent={PACKETS} received={ok_count} PDR={pdr:.1f}%")
    print(f"#   RTT mean={mean_rtt:.3f}ms SD={sd_rtt:.3f}ms")
    print(f"#   RTT P95={p95_rtt:.3f}ms P99={p99_rtt:.3f}ms")
    print(f"#   Jitter={jitter:.3f}ms")
    print()

def main():
    print("# RQ2 - Raw Wi-Fi Link Baseline Experiment")
    print("# Node: Initiator")
    print(f"# Target: {REFLECTOR_IP}:{PORT}")
    print("# seq,payload_bytes,RTT_ms,status")
    print()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_S)
    sock.bind(("", PORT + 1))  # bind to a different port for receiving

    # Wait a moment for reflector to be ready
    print("# Starting in 3 seconds...")
    time.sleep(3)

    for size in PAYLOAD_SIZES:
        run_test(sock, size)
        time.sleep(2)  # pause between payload size groups

    sock.close()
    print("# EXPERIMENT COMPLETE")

if __name__ == "__main__":
    main()