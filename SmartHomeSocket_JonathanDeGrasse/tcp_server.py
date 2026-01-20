import socket
import threading
import logging

HOST = "127.0.0.1"  # localhost
PORT = 5050         # TCP port

# Configure logging to file
logging.basicConfig(
    filename="server_log.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

devices = {}  # device_name -> {"type": ..., "addr": ..., "socket": ...}
devices_lock = threading.Lock()


def log(msg: str):
    """Log to both console and log file."""
    print(msg)
    logging.info(msg)


def handle_client(conn: socket.socket, addr):
    try:
        log(f"[Server] Connected to device at {addr}")

        # Receive registration message, e.g. "DEVICE Sensor01 TYPE temperature"
        raw = conn.recv(1024)
        if not raw:
            log(f"[Server] Empty registration from {addr}, closing.")
            return
        msg = raw.decode().strip()
        log(f"[Server] Received registration: {msg}")

        parts = msg.split()
        if len(parts) >= 4 and parts[0] == "DEVICE" and parts[2] == "TYPE":
            device_name = parts[1]
            device_type = parts[3]
        else:
            device_name = f"UnknownDevice_{addr[1]}"
            device_type = "unknown"
            log(f"[Server] Malformed registration from {addr}, using fallback name {device_name}")

        with devices_lock:
            devices[device_name] = {"type": device_type, "addr": addr, "socket": conn}

        log(f"[Server] Registered DEVICE={device_name} TYPE={device_type}")

        # Interaction loop for this device
        while True:
            # Ask user for a command for this device
            command = input(
                f"[Server] Enter command for {device_name} "
                f"(e.g., 'SET_INTERVAL 3' or 'ACTIVATE_ALARM', 'quit' to disconnect): "
            ).strip()

            if command.lower() == "quit":
                log(f"[Server] Closing connection with {device_name}")
                break

            if not command:
                continue

            try:
                conn.sendall(command.encode())
                log(f"[Server] Sent command to {device_name}: {command}")
            except OSError as e:
                log(f"[Server] Error sending to {device_name}: {e}")
                break

            # Wait for ACK
            try:
                conn.settimeout(10.0)  # seconds
                ack_data = conn.recv(1024)
                if not ack_data:
                    log(f"[Server] Connection closed while waiting for ACK from {device_name}")
                    break
                ack = ack_data.decode().strip()
                log(f"[Server] Received ACK from {device_name}: {ack}")
            except socket.timeout:
                log(f"[Server] Timeout waiting for ACK from {device_name}")
            finally:
                conn.settimeout(None)

    except Exception as e:
        log(f"[Server] Exception in client handler for {addr}: {e}")
    finally:
        with devices_lock:
            # Remove device if present
            for name, info in list(devices.items()):
                if info["addr"] == addr:
                    devices.pop(name, None)
                    break
        conn.close()
        log(f"[Server] Connection to {addr} closed.")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        log(f"[Server] TCP Smart Hub listening on {HOST}:{PORT}")

        while True:
            try:
                conn, addr = server_socket.accept()
            except OSError as e:
                log(f"[Server] Error on accept: {e}")
                break

            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )
            client_thread.start()


if __name__ == "__main__":
    main()