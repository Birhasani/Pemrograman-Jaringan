import socket

def main():
    host = '127.0.0.1'
    port = 45000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print(f"Connected to Time Server at {host}:{port}")

        while True:
            cmd = input("Enter command (TIME or QUIT): ").strip()
            if cmd not in ("TIME", "QUIT"):
                print("Hanya TIME atau QUIT.")
                continue
            sock.sendall((cmd + "\r\n").encode('utf-8'))

            resp = sock.recv(1024)
            if not resp:
                print("Server menutup koneksi.")
                break

            print("Response:", resp.decode().strip())
            if cmd == "QUIT":
                print("Keluar.")
                break

if __name__ == "__main__":
    main()
