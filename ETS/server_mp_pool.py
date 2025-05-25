import logging
import socket
import multiprocessing
from file_protocol import FileProtocol

# Inisialisasi pool proses
fp = FileProtocol()

SERVER_ADDRESS = ('0.0.0.0', 6667)
BUFFER_SIZE = 1024 * 1024

def process_client(connection, address, worker_status):
    d = ''
    try:
        while True:
            data = connection.recv(BUFFER_SIZE)
            if data:
                d += data.decode()
                if "\r\n\r\n" in d:
                    try:
                        hasil = fp.process_string(d.strip())
                        hasil = hasil + "\r\n\r\n"
                        connection.sendall(hasil.encode())
                        worker_status["success"] += 1
                    except Exception as e:
                        error_response = '{"status":"ERROR","data":"server error: %s"}\r\n\r\n' % str(e).replace('"', "'")
                        connection.sendall(error_response.encode())
                        worker_status["fail"] += 1
                    break
            else:
                break
    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")
        try:
            error_response = '{"status":"ERROR","data":"server fatal error: %s"}\r\n\r\n' % str(e).replace('"', "'")
            connection.sendall(error_response.encode())
        except Exception:
            pass
        worker_status["fail"] += 1
    finally:
        connection.close()


class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, max_workers=10):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.max_workers = max_workers
        
    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo} dengan max_workers={self.max_workers}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(10)

        manager = multiprocessing.Manager()
        worker_status = manager.dict({"success": 0, "fail": 0})

        with multiprocessing.Pool(processes=self.max_workers) as pool:
            try:
                while True:
                    connection, address = self.my_socket.accept()
                    logging.warning(f"Accepted connection from {address}")
                    # Menambahkan client baru ke dalam pool untuk diproses secara parallel
                    pool.apply_async(process_client, (connection, address, worker_status))
            except KeyboardInterrupt:
                logging.warning("Server shutting down.")
                logging.warning(f"Worker Success: {worker_status['success']}")
                logging.warning(f"Worker Fail: {worker_status['fail']}")
            finally:
                self.my_socket.close()

# Fungsi untuk menjalankan server
def main():
    max_workers = 10
    try:
        max_workers = int(input("Masukkan jumlah max workers server: "))
    except Exception:
        print("Input salah, menggunakan default max_workers=10")

    svr = Server(SERVER_ADDRESS[0], SERVER_ADDRESS[1], max_workers=max_workers)
    svr.run()

if __name__ == "__main__":
    main()
