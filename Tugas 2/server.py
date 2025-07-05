import socket
import threading
import logging
from datetime import datetime

logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(message)s')

class ProcessTheClient(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr

    def run(self):
        logging.warning(f"Client connected: {self.addr}")
        try:
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break
                msg = data.decode().strip()
                logging.warning(f"Received: {msg} from {self.addr}")

                if msg == "TIME":
                    now = datetime.now()
                    jam = now.strftime("%H:%M:%S")
                    resp = f"JAM {jam}\r\n"
                    self.conn.sendall(resp.encode('utf-8'))
                elif msg == "QUIT":
                    break
                else:
                    self.conn.sendall(b"ERROR: Unknown command\r\n")
        except Exception as e:
            logging.warning(f"Error with {self.addr}: {e}")
        finally:
            self.conn.close()
            logging.warning(f"Connection closed: {self.addr}")

class Server(threading.Thread):
    def __init__(self, host='0.0.0.0', port=45000):
        super().__init__(daemon=True)
        self.host = host
        self.port = port

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.bind((self.host, self.port))
            srv.listen(5)
            logging.warning(f"Server running on {self.host}:{self.port}")
            while True:
                conn, addr = srv.accept()
                ProcessTheClient(conn, addr).start()

def main():
    Server().start()
    threading.Event().wait()

if __name__ == "__main__":
    main()
