from socket import *
import socket
import time
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

# Fungsi untuk menangani klien yang datang
def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(32)  # Menunggu data dari klien
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv[-2:] == '\r\n':  # Menandakan akhir data
                    hasil = httpserver.proses(rcv)  # Proses request
                    hasil = hasil + "\r\n\r\n".encode()  # Mengakhiri respons dengan "\r\n\r\n"
                    connection.sendall(hasil)  # Kirim respons ke klien
                    rcv = ""
                    connection.close()
                    return
            else:
                break
        except OSError as e:
            pass
    connection.close()

# Fungsi utama server
def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Binding socket ke port dan alamat
    try:
        my_socket.bind(('0.0.0.0', 8885))  # Ganti port jika sudah terpakai
        print("Server bound to port 8885")
    except Exception as e:
        print(f"Failed to bind to port 8885: {e}")
        sys.exit(1)

    my_socket.listen(1)  # Server mulai mendengarkan koneksi
    print("Server is listening for connections...")

    # Menggunakan ThreadPoolExecutor untuk menangani banyak koneksi
    with ThreadPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()  # Menunggu koneksi
            print(f"Connection from {client_address}")
            # Proses klien dalam thread pool
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)

            # Menampilkan jumlah thread yang aktif
            jumlah = ['x' for i in the_clients if i.running() == True]
            print(f"Active threads: {len(jumlah)}")

# Menjalankan server
def main():
    Server()

if __name__ == "__main__":
    main()
