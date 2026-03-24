import RNS
import time
import os
import struct

PAYLOAD_SIZES = list(range(8, 248, 8))
OUTPUT_FILE   = "RQ6_packet_expansion.csv"

# We capture frames by patching the transport layer's send method
captured_frames = []

def capture_outgoing(data, iface):
    """Intercept every outgoing frame and record its size."""
    captured_frames.append(len(data))

def measure_expansion():
    print("# RQ6 - Reticulum Packet Expansion Ratio")
    print("# payload_bytes,frame_bytes,overhead_bytes,overhead_pct,expansion_ratio")

    # Minimal Reticulum config — no real interfaces
    config_dir = "/tmp/rq6_rns"
    os.makedirs(config_dir, exist_ok=True)

    config = """
[reticulum]
  enable_transport = False
  share_instance   = False

[logging]
  loglevel = 1
"""
    with open(f"{config_dir}/config", "w") as f:
        f.write(config)

    # Start Reticulum
    reticulum = RNS.Reticulum(configdir=config_dir)
    time.sleep(1)

    # Create destination identity
    dest_identity = RNS.Identity()
    destination   = RNS.Destination(
        dest_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        "rq6",
        "measure"
    )

    results = []

    for payload_size in PAYLOAD_SIZES:

        # Build payload of exact size
        payload = bytes([i % 256 for i in range(payload_size)])

        # Create the packet — this builds the complete Reticulum frame
        # including all headers, destination hash, and authentication tag
        packet = RNS.Packet(destination, payload)

        # Access the raw frame that Reticulum built
        # packet.raw contains the complete serialised frame
        packet.pack()
        frame_size  = len(packet.raw) if packet.raw else 0

        if frame_size > 0:
            overhead     = frame_size - payload_size
            overhead_pct = overhead / frame_size * 100.0
            expansion    = frame_size / payload_size

            print(f"{payload_size},{frame_size},{overhead},"
                  f"{overhead_pct:.1f},{expansion:.3f}")

            results.append((payload_size, frame_size, overhead,
                            overhead_pct, expansion))
        else:
            print(f"{payload_size},ERROR,ERROR,ERROR,ERROR")

        time.sleep(0.02)

    # Save CSV
    with open(OUTPUT_FILE, "w") as f:
        f.write("payload_bytes,frame_bytes,overhead_bytes,"
                "overhead_pct,expansion_ratio\n")
        for r in results:
            f.write(f"{r[0]},{r[1]},{r[2]},{r[3]:.1f},{r[4]:.3f}\n")

    print()
    print(f"# Results saved to {OUTPUT_FILE}")

    if results:
        overheads = [r[2] for r in results]
        print(f"# Fixed overhead: approximately {min(overheads)} bytes")
        print(f"# Overhead range: {min(overheads)} to {max(overheads)} bytes")
        print(f"# At 240B payload: {results[-1][3]:.1f}% overhead")

    print("# EXPERIMENT COMPLETE")

if __name__ == "__main__":
    measure_expansion()
