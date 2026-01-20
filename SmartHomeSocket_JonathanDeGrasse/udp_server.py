import socket
import logging

HOST = "127.0.0.1"
PORT = 6060

PACKETS_PER_CYCLE = 10

logging.basicConfig(
    filename="sensor_data_log.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def log(msg: str):
    print(msg)
    logging.info(msg)


def parse_packet(packet: str):
    """
    Expected format:
    Sensor01,2025-10-22 18:20:15,temperature,24.8,SEQ:5
    """
    try:
        parts = packet.strip().split(",")
        device_id = parts[0]
        timestamp = parts[1]
        sensor_type = parts[2]
        sensor_value = parts[3]
        seq_part = parts[4]  # "SEQ:5"
        seq_num = int(seq_part.split(":")[1])
        return device_id, timestamp, sensor_type, sensor_value, seq_num
    except Exception:
        return None, None, None, None, None


def main():
    # State per device: device_id -> {"packets": {seq: line}}
    device_state = {}

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, PORT))
        log(f"[UDP Server] Smart Hub Data Collector listening on {HOST}:{PORT}")

        while True:
            try:
                data, addr = sock.recvfrom(4096)
            except OSError as e:
                log(f"[UDP Server] Socket error on recvfrom: {e}")
                break

            line = data.decode().strip()
            log(f"[UDP Server] Received from {addr}: {line}")

            device_id, timestamp, sensor_type, sensor_value, seq = parse_packet(line)
            if device_id is None:
                log(f"[UDP Server] Malformed packet from {addr}: {line}")
                continue

            # Log raw data line (real sensor log)
            logging.info(f"DATA {line}")

            if device_id not in device_state:
                device_state[device_id] = {"packets": {}}

            state = device_state[device_id]
            state["packets"][seq] = line

            # Check if we have a full cycle
            count = len(state["packets"])
            if count >= PACKETS_PER_CYCLE:
                expected = set(range(1, PACKETS_PER_CYCLE + 1))
                received = set(state["packets"].keys())
                missing = sorted(expected - received)

                if not missing:
                    status_msg = f"STATUS RECEIVED {PACKETS_PER_CYCLE}/{PACKETS_PER_CYCLE} PACKETS"
                else:
                    status_msg = (
                        f"STATUS RECEIVED {len(received)}/{PACKETS_PER_CYCLE} PACKETS; "
                        f"MISSING: {missing}"
                    )

                try:
                    sock.sendto(status_msg.encode(), addr)
                    log(f"[UDP Server] Sent status to {device_id} at {addr}: {status_msg}")
                except OSError as e:
                    log(f"[UDP Server] Failed to send status to {addr}: {e}")

                # Start a new cycle for this device
                device_state[device_id] = {"packets": {}}


if __name__ == "__main__":
    main()
