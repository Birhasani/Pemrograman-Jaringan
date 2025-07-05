import sys
import socket
import json
import logging
import ssl
import os

server_address = ('localhost', 8885)

def make_socket(destination_address='localhost', port=8885):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def make_secure_socket(destination_address='localhost', port=8889):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def send_command(command_str, is_secure=False):
    sock = make_socket(server_address[0], server_address[1]) if not is_secure else make_secure_socket(server_address[0], server_address[1])
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
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

# Menampilkan Daftar File
def list_files():
    cmd = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    response = send_command(cmd)
    print(response)

# Mengunggah File
def upload_file(filename):
    with open(filename, 'rb') as f:
        file_data = f.read()
    cmd = f"POST /{filename} HTTP/1.1\r\nHost: localhost\r\nContent-Length: {len(file_data)}\r\n\r\n"
    response = send_command(cmd + file_data.decode())
    print(response)

# Menghapus File
def delete_file(filename):
    cmd = f"DELETE /{filename} HTTP/1.1\r\nHost: localhost\r\n\r\n"
    response = send_command(cmd)
    print(response)

def main():
    print("Pilih fitur yang ingin dijalankan:")
    print("1. Melihat daftar file")
    print("2. Mengunggah file")
    print("3. Menghapus file")

    pilihan = input("Masukkan pilihan (1/2/3): ")

    if pilihan == "1":
        list_files()  # Menampilkan daftar file
    elif pilihan == "2":
        filename = input("Masukkan nama file untuk diunggah: ")
        upload_file(filename)  # Mengunggah file
    elif pilihan == "3":
        filename = input("Masukkan nama file untuk dihapus: ")
        delete_file(filename)  # Menghapus file
    else:
        print("Pilihan tidak valid!")

if __name__ == '__main__':
    main()
