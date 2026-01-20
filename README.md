Project Info
SmartHomeSocket_Jonathan
By: Jonathan DeGrasse gtv9

This project simulates a Smart Home Monitoring and Control System
using TCP and UDP sockets in Python.

FILES:
- tcp_server.py     → Smart Hub (control center)
- tcp_client.py     → IoT device client for control commands
- udp_server.py     → Smart Hub (data collector)
- udp_client.py     → IoT device client for sensor data
- report.pdf        → Design explanation, screenshots, and logs

RUN INFO:

1. Start TCP Server:
   python tcp_server.py

2. Start one or more TCP Clients:
   python tcp_client.py

3. Start UDP Server:
   python udp_server.py

4. Start UDP Client(s):
   python udp_client.py

All logs are saved automatically:
- server_log.txt
- sensor_data_log.txt
