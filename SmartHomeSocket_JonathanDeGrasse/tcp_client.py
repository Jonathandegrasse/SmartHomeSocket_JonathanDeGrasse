import socket

HOST = "127.0.0.1"
PORT = 5050

DEVICE_NAME = "Sensor01"
DEVICE_TYPE = "temperature"


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((HOST, PORT))
            print(f"[{DEVICE_NAME}] Connected to Smart Hub at {HOST}:{PORT}")
        except OSError as e:
            print(f"[{DEVICE_NAME}] Connection failed: {e}")
            return

        # Send registration
        registration_msg = f"DEVICE {DEVICE_NAME} TYPE {DEVICE_TYPE}"
        try:
            sock.sendall(registration_msg.encode())
            print(f"[{DEVICE_NAME}] Sent registration: {registration_msg}")
        except OSError as e:
            print(f"[{DEVICE_NAME}] Failed to send registration: {e}")
            return

        # Command handling loop
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    print(f"[{DEVICE_NAME}] Server closed connection.")
                    break

                command = data.decode().strip()
                print(f"[{DEVICE_NAME}] Received command: {command}")

                # Simulate execution of the command
                if command.startswith("SET_INTERVAL"):
                    try:
                        interval = int(command.split()[1])
                        print(
                            f"[{DEVICE_NAME}] Changing reporting interval to "
                            f"{interval} seconds (simulated)."
                        )
                    except (IndexError, ValueError):
                        print(f"[{DEVICE_NAME}] Malformed SET_INTERVAL command.")
                elif command == "ACTIVATE_ALARM":
                    print(f"[{DEVICE_NAME}] Alarm activated (simulated).")
                else:
                    print(f"[{DEVICE_NAME}] Executing generic command: {command}")

                # Send ACK
                ack_msg = "ACK Command Executed"
                try:
                    sock.sendall(ack_msg.encode())
                    print(f"[{DEVICE_NAME}] Sent ACK.")
                except OSError as e:
                    print(f"[{DEVICE_NAME}] Failed to send ACK: {e}")
                    break

            except KeyboardInterrupt:
                print(f"[{DEVICE_NAME}] Interrupted by user.")
                break
            except OSError as e:
                print(f"[{DEVICE_NAME}] Socket error: {e}")
                break

        print(f"[{DEVICE_NAME}] Closing connection.")


if __name__ == "__main__":
    main()
