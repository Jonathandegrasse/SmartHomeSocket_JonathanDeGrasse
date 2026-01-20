import socket
import time
from datetime import datetime
import random

HOST = "127.0.0.1"
PORT = 6060

DEVICE_ID = "Sensor01"
SENSOR_TYPE = "temperature"
PACKETS_PER_CYCLE = 10
REPORT_INTERVAL = 2  # seconds between packets


def build_packet(seq: int) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Simulate a temperature between 20.0 and 30.0
    value = round(random.uniform(20.0, 30.0), 1)
    return f"{DEVICE_ID},{timestamp},{SENSOR_TYPE},{value},SEQ:{seq}"


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5.0)  # timeout waiting for status

        hub_addr = (HOST, PORT)
        print(f"[{DEVICE_ID}] UDP client sending to Smart Hub at {HOST}:{PORT}")

        while True:
            # Send one cycle of packets
            for seq in range(1, PACKETS_PER_CYCLE + 1):
                packet = build_packet(seq)
                try:
                    sock.sendto(packet.encode(), hub_addr)
                    print(
                        f"[{DEVICE_ID}] Sending packet SEQ:{seq} — "
                        f"{SENSOR_TYPE}={packet.split(',')[3]}"
                    )
                except OSError as e:
                    print(f"[{DEVICE_ID}] Failed to send packet SEQ:{seq}: {e}")
                time.sleep(REPORT_INTERVAL)

            # Wait for status acknowledgement
            try:
                status_data, _ = sock.recvfrom(1024)
                status_msg = status_data.decode().strip()
                print(f"[{DEVICE_ID}] {status_msg}")
            except socket.timeout:
                print(f"[{DEVICE_ID}] No status received from server (timeout).")
            except OSError as e:
                print(f"[{DEVICE_ID}] Error while waiting for status: {e}")

            # Small pause before starting the next cycle
            print(f"[{DEVICE_ID}] Cycle complete. Starting a new cycle...\n")
            time.sleep(3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"[{DEVICE_ID}] Stopped by user.")
