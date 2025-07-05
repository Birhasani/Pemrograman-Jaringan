from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

# Untuk menggunakan processpoolexecutor, class ProcessTheClient dirubah menjadi function
def ProcessTheClient(connection, address):
    print(f"Handling client from {address}")  # Menambahkan log untuk debugging
    rcv = ""
    while True:
        try:
            data = connection.recv(32)
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv[-2:] == '\r\n':
                    hasil = httpserver.proses(rcv)
                    hasil = hasil + "\r\n\r\n".encode()
                    connection.sendall(hasil)
                    rcv = ""
                    connection.close()
                    return
            else:
                break
        except OSError as e:
            pass
    connection.close()

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Mencoba untuk bind ke alamat dan port
    try:
        my_socket.bind(('0.0.0.0', 8889))
        print("Server bound to port 8889")
    except Exception as e:
        print(f"Failed to bind to port 8889: {e}")
        sys.exit(1)

    my_socket.listen(1)
    print("Server is listening for connections...")

    with ProcessPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            print(f"Connection from {client_address}")
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)
            jumlah = ['x' for i in the_clients if i.running() == True]
            print(f"Active processes: {len(jumlah)}")

def main():
    Server()

if __name__ == "__main__":
    main()
