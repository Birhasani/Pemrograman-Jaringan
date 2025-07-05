import sys
import socket
import logging
import ssl
import os

# Server address and port
server_address = ('localhost', 8889)

# Function to create a basic socket
def make_socket(destination_address='localhost', port=8889):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"Connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"Error {str(ee)}")

# Function to create a secure socket with SSL
def make_secure_socket(destination_address='localhost', port=8889):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_verify_locations(os.getcwd() + '/domain.crt')  # Ensure the certificate file is in the correct location

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"Connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"Error {str(ee)}")

def send_command(command_str, is_secure=False):
    sock = make_socket(server_address[0], server_address[1]) if not is_secure else make_secure_socket(server_address[0], server_address[1])
    try:
        logging.warning(f"sending message")
        sock.sendall(command_str)  # Send the entire byte string directly
        logging.warning(command_str)

        data_received = ""
        while True:
            data = sock.recv(2048)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = data_received
        logging.warning("data received from server:")
        return hasil
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return False

def upload_file(filename):
    try:
        # Read the file in binary mode
        with open(filename, 'rb') as f:
            file_data = f.read()

        # Build HTTP POST header
        cmd = f"POST /{filename} HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(file_data)}\r\n\r\n"
        
        # Encode the header to bytes and combine it with the file data
        cmd_bytes = cmd.encode()
        
        # Send both the HTTP command header and the file data as one byte string
        response = send_command(cmd_bytes + file_data)  # Sending combined byte data
        print(response)

    except FileNotFoundError as e:
        print(f"File '{filename}' not found. Please check the file path.")


def list_files():
    cmd = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    response = send_command(cmd.encode())  # Encode the command string to bytes
    print(response)

def delete_file(filename):
    cmd = f"DELETE /{filename} HTTP/1.1\r\nHost: localhost\r\n\r\n"
    response = send_command(cmd.encode())  # Encode the command string to bytes
    print(response)


# Main function to run the client
def main():
    print("Pilih fitur yang ingin dijalankan:")
    print("1. Melihat daftar file")
    print("2. Mengunggah file")
    print("3. Menghapus file")

    pilihan = input("Masukkan pilihan (1/2/3): ")

    if pilihan == "1":
        list_files()  # List files
    elif pilihan == "2":
        filename = input("Masukkan nama file untuk diunggah: ")
        upload_file(filename)  # Upload file
    elif pilihan == "3":
        filename = input("Masukkan nama file untuk dihapus: ")
        delete_file(filename)  # Delete file
    else:
        print("Pilihan tidak valid!")

if __name__ == '__main__':
    main()
