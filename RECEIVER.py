import socket
import time

PORT = 5005

def main():
    print("# RQ2 - Raw Wi-Fi Link Baseline Experiment")
    print("# Node: Reflector")
    print(f"# Listening on UDP port {PORT}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))

    total_received = 0
    total_echoed   = 0

    print("# Reflector ready - waiting for packets")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            total_received += 1

            # Echo back immediately unchanged
            sock.sendto(data, addr)
            total_echoed += 1

            # Log every received packet
            seq = (data[0] << 8) | data[1] if len(data) >= 2 else 0
            print(f"# RX seq={seq} len={len(data)} "
                  f"from={addr[0]} "
                  f"rx={total_received} echoed={total_echoed}")

        except KeyboardInterrupt:
            print("# Reflector stopped")
            break

    sock.close()

if __name__ == "__main__":
    main()