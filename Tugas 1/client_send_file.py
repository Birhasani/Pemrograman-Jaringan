import sys
import socket
import logging
import os

# Set basic logging
logging.basicConfig(level=logging.INFO)

try:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('172.16.16.101', 32444)
    logging.info(f"connecting to {server_address}")
    sock.connect(server_address)

    # Read the file content to be sent
    filename = 'data.txt'
    if not os.path.exists(filename):
        logging.info(f"ERROR: File '{filename}' not found.")
        exit(0)

    with open(filename, 'rb') as f:
        file_data = f.read()

    logging.info(f"sending file '{filename}' with size {len(file_data)} bytes")
    sock.sendall(file_data)

    # Receive the echo from server
    amount_received = 0
    amount_expected = len(file_data)
    while amount_received < amount_expected:
        data = sock.recv(1024)
        amount_received += len(data)
        logging.info(f"received {len(data)} bytes")
        
except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
    exit(0)
finally:
    logging.info("closing")
    sock.close()
